# Railway Deployment Guide

## Current Setup

Your backend is configured to deploy to Railway at:
**https://max-backend-production.up.railway.app**

Your frontend is already deployed on Vercel at:
**https://realwin-frontend-master.vercel.app**

## Changes Made for Production

### 1. CORS Configuration Updated
- Added both Vercel URLs to allowed origins
- Backend will accept requests from production frontend

### 2. Subscription Checks Disabled
- All authenticated users have full access
- No payment required

### 3. Login Endpoint Fixed
- Now accepts JSON instead of form data
- Compatible with frontend API client

## Deploy to Railway

### Option 1: Using Railway CLI

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

### Option 2: Using Git Push

```bash
# Add all changes
git add .

# Commit changes
git commit -m "Fix auth endpoints and disable subscription checks"

# Push to Railway (if connected via GitHub)
git push origin main
```

### Option 3: Using Railway Dashboard

1. Go to https://railway.app
2. Login to your account
3. Find your project: "max-backend-production"
4. Click "Deploy" or it will auto-deploy if GitHub is connected

## Environment Variables on Railway

Make sure these are set in Railway dashboard:

### Required Variables
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
DEBUG=false
APP_ENV=production
```

### Database Variables (Already Set)
```
DB_HOST=realwin.czgiwmwqcexk.eu-west-2.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgrespassword
DB_PORT=5432
```

### Frontend URLs (Already Set)
```
FRONTEND_URL=https://realwin-frontend-master.vercel.app
CORS_ORIGINS=https://realwin-frontend-master.vercel.app,https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
```

### API Keys (Already Set)
```
OPENAI_API_KEY=sk-proj-...
CRICKET_API_KEY=RS5:836fe0c1a85d44000f7ebe67f9d730c4
CRICKET_PROJECT_ID=RS_P_1942111570733699074
FOOTBALL_API_TOKEN=7O6SVG55TP0z3aK9uZKcM2zKJ90pdTemHBViFl5GFpUazz8NyjPlR2C7ygey
```

## Verify Deployment

### 1. Check Backend Health
```bash
curl https://max-backend-production.up.railway.app/health
```

Expected response:
```json
{"api": true, "database": true}
```

### 2. Check API Documentation
Open: https://max-backend-production.up.railway.app/docs

### 3. Test Authentication
```bash
# Signup
curl -X POST https://max-backend-production.up.railway.app/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST https://max-backend-production.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 4. Test Frontend Connection
1. Go to https://realwin-frontend-master.vercel.app
2. Click "Sign Up"
3. Create an account
4. You should be logged in automatically
5. Navigate to predictions - should work without subscription!

## Database Migrations

If you need to run migrations on Railway:

```bash
# Using Railway CLI
railway run alembic upgrade head

# Or connect to Railway shell
railway shell
alembic upgrade head
```

## Monitoring

### Check Logs
```bash
# Using Railway CLI
railway logs

# Or view in Railway dashboard
# https://railway.app -> Your Project -> Deployments -> View Logs
```

### Check Deployment Status
```bash
railway status
```

## Troubleshooting

### Backend Not Responding
1. Check Railway logs: `railway logs`
2. Verify environment variables are set
3. Check database connection
4. Ensure PORT is not hardcoded (Railway provides $PORT)

### CORS Errors
1. Verify CORS origins in `source/main.py`
2. Check Railway environment variables
3. Redeploy after changes

### Database Connection Issues
1. Check DATABASE_URL or DB_* variables
2. Verify database is accessible from Railway
3. Check database credentials
4. Run migrations: `railway run alembic upgrade head`

### Authentication Errors
1. Check SECRET_KEY is set
2. Verify JWT token generation
3. Check user is created with active=True
4. Review backend logs

## Post-Deployment Checklist

- [ ] Backend health check passes
- [ ] API documentation accessible
- [ ] Can create new user account
- [ ] Can login with credentials
- [ ] Frontend can connect to backend
- [ ] Predictions are accessible
- [ ] No subscription prompts shown
- [ ] CORS working correctly
- [ ] Database migrations applied
- [ ] Environment variables set

## Quick Deploy Commands

```bash
# Full deployment workflow
git add .
git commit -m "Deploy backend updates"
git push origin main

# Or using Railway CLI
railway up

# Check deployment
railway logs --follow
```

## Production URLs

- **Frontend**: https://realwin-frontend-master.vercel.app
- **Backend API**: https://max-backend-production.up.railway.app
- **API Docs**: https://max-backend-production.up.railway.app/docs
- **Health Check**: https://max-backend-production.up.railway.app/health

## Important Notes

✅ **Subscription checks are disabled** - All users have full access
✅ **CORS configured** for both Vercel URLs
✅ **Auth endpoints fixed** to accept JSON
✅ **Users active by default** on signup
✅ **Database already configured** on AWS RDS

## Next Steps

1. **Deploy to Railway** using one of the methods above
2. **Test the deployment** using the verification steps
3. **Monitor logs** for any issues
4. **Test frontend** at https://realwin-frontend-master.vercel.app

Your production environment is ready to go! 🚀
