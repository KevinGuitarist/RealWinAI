# Development Test User Setup

## Quick Setup for Testing Premium Features

I've created a development endpoint to quickly set up a test user with premium subscription access.

### Test User Credentials
- **Email:** `vaibhav@premium.com`
- **Password:** `123456`
- **Status:** Premium Active (365 days)

---

## How to Create the Test User

### Option 1: Using the API Endpoint (Easiest)

1. **Make sure your backend is running** (locally or on Railway)

2. **Call the dev endpoint:**

```bash
# If running locally:
curl -X POST http://localhost:8000/dev/create-test-user

# If using Railway backend:
curl -X POST https://max-backend-production.up.railway.app/dev/create-test-user
```

3. **Login with the credentials:**
   - Email: `vaibhav@premium.com`
   - Password: `123456`

### Option 2: Using your browser

Simply visit one of these URLs in your browser:
- Local: http://localhost:8000/dev/create-test-user
- Railway: https://max-backend-production.up.railway.app/dev/create-test-user

You'll see a JSON response confirming the user was created.

---

## What Gets Created

- ✅ User account with verified email
- ✅ Active premium subscription
- ✅ Subscription valid for 365 days
- ✅ Full access to all premium features

---

## Important Notes

⚠️ **This is for DEVELOPMENT TESTING ONLY!**

- The endpoint only works when `DEBUG=True` in your environment
- DO NOT enable this in production
- The endpoint will return a 403 error if DEBUG is disabled

---

## Environment Variables

Make sure your backend has `DEBUG=True` set:

```env
DEBUG=true
```

For production deployments, set `DEBUG=false` to disable this endpoint.

---

## Testing the Connection

After creating the user, test the login:

1. Go to your frontend: https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app
2. Click "Login"
3. Enter:
   - Email: `vaibhav@premium.com`
   - Password: `123456`
4. You should have full premium access!

---

## Troubleshooting

**Endpoint returns 403 Forbidden:**
- Make sure `DEBUG=true` is set in your environment variables

**User already exists:**
- The endpoint will update the existing user's subscription to active
- Safe to call multiple times

**Can't connect to backend:**
- Make sure your backend is running
- Check that CORS is properly configured for your frontend URL
