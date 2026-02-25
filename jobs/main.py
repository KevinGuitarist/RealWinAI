#!/usr/bin/env python3
import sys
import os
import json
import psycopg2
from datetime import datetime,timedelta
from helper.cricket_prediction import get_cricket_pred
from helper.cricket import (
    get_top5_cricket_predictions_for_date,
)
from helper.football import get_top5_predictions_for_date as get_top5_football_predictions,fetch_all_matches_for_date,get_rich_match_prediction
from helper.cricket_tournaments import get_tournament_matches
from psycopg2.extras import Json
from helper.prediction import get_cricket_predictions


with open("matches.json", "r") as f:
    cricket_matches = json.load(f)

def get_db_connection():
    """
    Establish a connection to Postgres using environment variables or default values.
    """
    host = os.getenv('DB_HOST', 'admin.c8jg2isskfxo.us-east-1.rds.amazonaws.com')
    port = int(os.getenv('DB_PORT', '5432'))
    dbname = os.getenv('DB_NAME', 'realwin-prod')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'sT6WL3YodPq0LoYTKug9')

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to Postgres: {e}", file=sys.stderr)
        sys.exit(1)

def ensure_table_exists(conn):
    """
    Create the cricket_predictions table if it does not exist.
    Columns:
      - id: SERIAL PRIMARY KEY
      - key: VARCHAR(255) NOT NULL UNIQUE
      - prediction: JSON NOT NULL
      - date: VARCHAR(10) DEFAULT NULL
      - created_at: TIMESTAMP DEFAULT NOW()
    """
    table_ddl = """
    CREATE TABLE IF NOT EXISTS cricket_predictions (
      id SERIAL PRIMARY KEY,
      key VARCHAR(255) NOT NULL UNIQUE,
      prediction JSON NOT NULL,
      date VARCHAR(10) DEFAULT NULL,
      created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(table_ddl)
        conn.commit()
    except Exception as e:
        print(f"❌ Failed to ensure table exists: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)

def fetch_cricket_predictions(today):
    """
    Fetch cricket predictions for today.
    Returns a dict containing predictions, date, message, data_source, total_predictions, and optional history.
    """
    resp = get_top5_cricket_predictions_for_date(today)
    predictions = resp.get("predictions")

    return {"predictions": predictions, "date": today, "message": f"Successfully retrieved {len(predictions)} cricket predictions", "data_source": "Real Cricket API (Sports.roanuz.com)", "total_predictions": len(predictions)}


def fetch_football_predictions(today):

    print("====== Football Predictions =======")
    """
    Fetch football predictions for today with fallback support.
    Returns a list of prediction dicts.
    """
    try:
        predictions = get_top5_football_predictions(today)
    except Exception as e:
        print(f"⚠️ Football API error: {e}", file=sys.stderr)
    return {"predictions": predictions, "date": today }

import json
import sys
from psycopg2.extras import execute_values

def store_cricket_predictions(conn, result,date):

    
    """
    Upsert into cricket_predictions on 'key' conflict,
    updating prediction and date each time.
    """
    # Note: quoting "key" because it's a reserved word
    upsert_sql = """
    INSERT INTO cricket_predictions ("key", prediction, date)
    VALUES %s
    ON CONFLICT ("key") DO UPDATE
      SET prediction = EXCLUDED.prediction,
          date       = EXCLUDED.date
    RETURNING
      (xmax = 0) AS inserted,  -- True if it was an INSERT
      (xmax <> 0) AS updated;  -- True if it was an UPDATE
    """

    # prepare list of tuples
    rows = []
    # print("==== Results ====")
    # print(result)
    for item in result:
        match = item
        prediction = item
        payload = {
            "match":match,
            "prediction": prediction
        }
        # skip missing key
        key_val = match["match_info"]["match_key"]
        if not key_val:
            continue
        rows.append((key_val,Json(payload), date))

    if not rows:
        return  # nothing to do

    try:
        with conn.cursor() as cur:
            # batch upsert
            execute_values(cur, upsert_sql, rows)
            # fetch the RETURNING results to see what happened
            results = cur.fetchall()
        conn.commit()

        # count how many INSERT vs UPDATE
        inserted = sum(1 for ins, _ in results if ins)
        updated  = sum(1 for _, upd in results if upd)
        print(f"Inserted: {inserted}, Updated: {updated}")

    except Exception as e:
        print(f"❌ Failed to store predictions: {e}", file=sys.stderr)
        conn.rollback()


def store_football_predictions(conn, result):
    print(f"Store : {result}")
    """
    Store each prediction into cricket_predictions table, avoiding duplicates by unique key.
    """
    insert_sql = (
        "INSERT INTO football_predictions (key, prediction, date)"
        " VALUES (%s, %s, %s)"
        " ON CONFLICT (key) DO NOTHING"
    )
    try:
        with conn.cursor() as cur:
            for pred in result.get('predictions', []):
                key_val = pred.get('id')
                if pred.get("prediction") == False:
                    continue
                if not key_val:
                    continue
                cur.execute(insert_sql,
                            (key_val, json.dumps(pred), result.get('date')))
        conn.commit()
    except Exception as e:
        print(f"❌ Failed to store predictions: {e}", file=sys.stderr)
        conn.rollback()

def main():

    today    = datetime.now().strftime('%Y-%m-%d')

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


    conn = get_db_connection()
    # ensure_table_exists(conn)
    try:
        # cricket_result = get_cricket_predictions(today)

        
        # filtered_matches = [
        #     m for m in cricket_result
        #     if m.get("match_info", {}).get("match_date") == today
        # ]

        # store_cricket_predictions(conn, filtered_matches,today)

        # # football predictions

        # football_predictions = fetch_football_predictions(today)
        # store_football_predictions(conn, football_predictions)


        matches = fetch_all_matches_for_date(today)
        print(f"=== football Matches === {len(matches)}")
        # print(matches)
        if not matches:
            print(f"No matches found for date: {today}")
            return []
        
       
        league_cache = {}
        failed_attempts = 0
        max_failures = 3  # Stop after 3 consecutive failures
        
        for match in matches:
            predictions = []
            print(f"Match ID  : {match.get("id")}")

            try:
                rich_pred = get_rich_match_prediction(match, league_cache)
                if rich_pred:
                    predictions.append(rich_pred)
                    _data = {"predictions": predictions, "date": today }
                    store_football_predictions(conn, _data)
                    failed_attempts = 0  # Reset failure counter on success
                else:
                    failed_attempts += 1
                    if failed_attempts >= max_failures:
                        print(f"Too many failures ({failed_attempts}), stopping prediction generation")
                        break
            except Exception as e:
                print(f"Error in rich prediction for match {match.get('id', 'unknown')}: {e}")
                failed_attempts += 1
                if failed_attempts >= max_failures:
                    print(f"Too many failures ({failed_attempts}), stopping prediction generation")
                    break
                continue

        sys.exit(0)

    except Exception as e:
        print(f"❌ Unhandled error: {e}", file=sys.stderr)
        conn.close()
        _, _, tb = sys.exc_info()
        # if you want the deepest frame (where it actually failed), walk to the end:
        while tb.tb_next:
            tb = tb.tb_next
        line_no = tb.tb_lineno
        print(f"❌ Error in sync  at line {line_no}: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()