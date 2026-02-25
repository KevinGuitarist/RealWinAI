import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load secrets from environment variables. Set these in your .env file or system environment.
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
OPENAI_API_KEY ='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'
API_TOKEN = os.getenv('API_TOKEN', 'EowWj4NnMhCihlx2acWj13J4AXSYpJJtPXjCcMM9BprYsttIl1PlcMHPAVcg')

# Cricket API Configuration
CRICKET_API_KEY = os.getenv("CRICKET_API_KEY", "RS5:836fe0c1a85d44000f7ebe67f9d730c4")
CRICKET_PROJECT_ID = os.getenv("CRICKET_PROJECT_ID", "RS_P_1942111570733699074")

# Football API Configuration
FOOTBALL_API_TOKEN = os.getenv("FOOTBALL_API_TOKEN", "7O6SVG55TP0z3aK9uZKcM2zKJ90pdTemHBViFl5GFpUazz8NyjPlR2C7ygey")

# Revolut Payment Configuration
REVOLUT_SECRET_KEY = "sk_2MEVdU2B_qN3ZMx-HbEiuWLCCQF-6K5YHa4HCc-W39hKHGrD15L5dWBS7mFkFI17"
REVOLUT_PUBLIC_KEY = "pk_wYuIImqRlIk3a87Gyf10Wrhwjx2b2G5fNaK4kS3qdjIeLZfp"
REVOLUT_API_URL = "https://merchant.revolut.com/api"
# REVOLUT_API_URL="https://sandbox-merchant.revolut.com/api"

# Subscription Configuration
SUBSCRIPTION_PRICE = 19.99  # GBP per month
SUBSCRIPTION_CURRENCY = "GBP"

# Database configuration: load from environment, fallback to production defaults
DB_HOST = os.getenv('DB_HOST', 'realwin.czgiwmwqcexk.eu-west-2.rds.amazonaws.com')
DB_NAME = os.getenv('DB_NAME', 'postgres')
print(DB_NAME)
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgrespassword')
DB_PORT = int(os.getenv('DB_PORT', 5432))

def db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )