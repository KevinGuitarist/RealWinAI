# Backend-Frontend Connection Guide

## Changes Made

Your backend has been updated to connect with your deployed frontend at:
`https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app`

### Updated Files:
- `source/main.py` - Added new frontend URL to CORS origins
- `source/core/settings.py` - Updated Stripe redirect URLs
- `source/core/mailer.py` - Updated password reset URL
- `source/app/payments/views.py` - Updated payment success URL
- `scripts/pythonanywhere_deploy.sh` - Updated deployment script
- `railway.toml` - Updated Railway configuration
- `render.yaml` - Updated Render configuration

## Deployment Steps

### 1. Environment Variables
Make sure your deployment platform has these environment variables set:

```bash
FRONTEND_URL=https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
CORS_ORIGINS=https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
```

### 2. Deploy to Your Platform

#### For Render:
```bash
git add .
git commit -m "Update frontend URL configuration"
git push origin main
```
Render will automatically deploy the changes.

#### For Railway:
```bash
git add .
git commit -m "Update frontend URL configuration"
git push origin main
```
Railway will automatically deploy the changes.

#### For PythonAnywhere:
```bash
./scripts/pythonanywhere_deploy.sh
```

### 3. Verify Connection
After deployment, test the connection by:
1. Opening your frontend: https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
2. Try logging in or making API calls
3. Check browser console for any CORS errors

## Frontend Configuration
Make sure your frontend is configured to call your backend API. The frontend should have the backend URL configured in its environment variables or configuration files.

## Troubleshooting

### CORS Issues
If you see CORS errors in the browser console:
1. Verify the frontend URL is exactly correct in the backend CORS configuration
2. Check that your backend is deployed with the updated configuration
3. Ensure the frontend is making requests to the correct backend URL

### API Connection Issues
1. Check that your backend is running and accessible
2. Verify the API endpoints are working by testing them directly
3. Check the network tab in browser dev tools for failed requests

## Next Steps
1. Deploy your backend with the updated configuration
2. Test the connection between frontend and backend
3. Monitor for any errors in production logs