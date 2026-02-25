#!/bin/bash

# Environment variables
export OPENAI_API_KEY='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'
export CRICKET_API_KEY='RS5:836fe0c1a85d44000f7ebe67f9d730c4'
export CRICKET_PROJECT_ID='RS_P_1942111570733699074'
export FOOTBALL_API_TOKEN='7O6SVG55TP0z3aK9uZKcM2zKJ90pdTemHBViFl5GFpUazz8NyjPlR2C7ygey'
export APP_ENV='production'
export FRONTEND_URL='https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app'
export CORS_ORIGINS='https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app'
export DB_HOST='realwin.czgiwmwqcexk.eu-west-2.rds.amazonaws.com'
export DB_NAME='postgres'
export DB_USER='postgres'
export DB_PASSWORD='postgrespassword'
export DB_PORT='5432'

# Update PATH for Python 3.12
PATH=$HOME/.local/bin:$PATH
export PATH

# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application with uvicorn
uvicorn source.main:app --host 0.0.0.0 --port 8000