#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploying MAX System...${NC}"

# Navigate to project root
cd "$(dirname "$0")/.."

# 1. Setup Python environment
echo -e "\n${YELLOW}📦 Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Build frontend
echo -e "\n${YELLOW}🔨 Building frontend...${NC}"
cd realwin-frontend-master
npm install
npm run build
cd ..

# 3. Start backend server
echo -e "\n${YELLOW}🌐 Starting backend server...${NC}"
uvicorn source.main:app --host 0.0.0.0 --port 8000 --reload

echo -e "\n${GREEN}✅ Deployment complete!${NC}"
echo -e "MAX is now available at: ${YELLOW}http://localhost:8000${NC}"