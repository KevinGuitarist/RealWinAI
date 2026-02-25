# Quick Deployment Guide

## Your Backend URLs

### Current Configuration:
- **Render URL**: https://max-betting-ai.onrender.com
- **Frontend URL**: https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app

## Deployment Options

### Option 1: Render (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Connect your GitHub repository: `https://github.com/Vaibhav05-edu/RealWinAIMAX.git`
3. Create a new Web Service
4. Use these settings:
   - **Build Command**: `pip install -U pip && pip install poetry==1.4.2 && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main`
   - **Start Command**: `uvicorn source.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.9
   - **Auto-Deploy**: Yes

### Option 2: Railway
1. Go to [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Deploy - Railway will use the `railway.toml` configuration automatically

### Option 3: Vercel (Quick Alternative)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

## Environment Variables Needed
Make sure to set these in your deployment platform:

```
FRONTEND_URL=https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
CORS_ORIGINS=https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
DB_HOST=realwin.czgiwmwqcexk.eu-west-2.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgrespassword
DB_PORT=5432
SECRET_KEY=realwin_max_secure_jwt_secret_key_2024
APP_ENV=production
```

## Testing Your Deployment
Once deployed, test these endpoints:
- `{YOUR_BACKEND_URL}/health` - Health check
- `{YOUR_BACKEND_URL}/docs` - API documentation
- `{YOUR_BACKEND_URL}/` - Should redirect to chat

## Frontend Connection
Update your frontend to use your backend URL for API calls.