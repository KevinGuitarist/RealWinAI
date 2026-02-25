#!/usr/bin/env python3
import sys
import os
import json
import psycopg2
import json
import sys
from psycopg2.extras import execute_values
from datetime import datetime,timedelta
from psycopg2.extras import Json
from prediction import get_cricket_predictions


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


def main():

    today    = datetime.now().strftime('%Y-%m-%d')

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')


    conn = get_db_connection()
    # ensure_table_exists(conn)
    try:
        cricket_result = get_cricket_predictions(today)

        
        filtered_matches = [
            m for m in cricket_result
            if m.get("match_info", {}).get("match_date") == today
        ]

        store_cricket_predictions(conn, filtered_matches,today)

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