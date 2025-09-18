# Manual Railway Deployment Steps

Since the CLI requires browser authentication, here are the manual steps to complete your deployment:

## 🔐 Step 1: Login to Railway

1. **Visit the login URL**: https://railway.com/cli-login?d=d29yZENvZGU9b3JjaGlkLWNsZXZlci1ub3VyaXNobWVudCZob3N0bmFtZT1Jb3JpSW1hc3U=
2. **Use pairing code**: `orchid-clever-nourishment`
3. **Complete the login** in your browser

## 🚀 Step 2: Deploy Your Services

### Option A: Using Railway Web Interface (Recommended)

1. **Go to [railway.app](https://railway.app)**
2. **Create New Project** → "Deploy from GitHub repo"
3. **Select this repository**: `Rmgfr`
4. **Deploy API Service**:
   - Root Directory: `platform/api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. **Deploy Web Service**:
   - Root Directory: `platform/web`
   - Build Command: `pnpm install && pnpm run build`
   - Start Command: `pnpm run start`

### Option B: Using CLI (After Login)

```powershell
# Set environment variables
$env:RAILWAY_TOKEN = "888d5ae2-0b3a-41d7-ad1f-9fbf07ba1c5b"
$env:DATABASE_URL = "postgresql://postgres:NxPtrsFizMmZKahSOJNQPLtHKbCQnzsR@hopper.proxy.rlwy.net:32920/railway"

# Login (complete in browser)
railway login --browserless

# Create project
railway project new "anti-fraud-platform"

# Add PostgreSQL database
railway add postgresql

# Set environment variables
railway variables --set "DATABASE_URL=$env:DATABASE_URL"
railway variables --set "ENVIRONMENT=production"
railway variables --set "API_SECRET_KEY=your-secret-key-here"

# Deploy API
cd api
railway up

# Deploy Web (in new terminal)
cd ../web
railway up
```

## 🗄️ Step 3: Apply Database Schema

### Option A: Using Railway Database Console

1. **Go to your Railway project dashboard**
2. **Click on your PostgreSQL service**
3. **Open the database console**
4. **Copy and paste the contents of `platform/railway-db-setup.sql`**
5. **Execute the SQL**

### Option B: Using External Tool

If you have `psql` installed:
```bash
psql "postgresql://postgres:NxPtrsFizMmZKahSOJNQPLtHKbCQnzsR@hopper.proxy.rlwy.net:32920/railway" -f platform/railway-db-setup.sql
```

## 🧪 Step 4: Test Your Deployment

```powershell
# Test database connectivity
node test-db.js

# Test API endpoints (replace with your actual URL)
$env:BASE_URL = "https://your-api-domain.railway.app"
$env:ENDPOINTS_JSON = '["/health","/docs","/"]'
npm run verify:deployment
```

## 🔧 Step 5: Configure Environment Variables

### API Service Variables:
```
DATABASE_URL=postgresql://postgres:NxPtrsFizMmZKahSOJNQPLtHKbCQnzsR@hopper.proxy.rlwy.net:32920/railway
ENVIRONMENT=production
API_SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://your-web-domain.railway.app
TRUSTED_HOSTS=localhost,*.vercel.app,*.supabase.co,*.railway.app
```

### Web Service Variables:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-key
CLERK_SECRET_KEY=your-clerk-secret
```

## 🆘 Troubleshooting

### If Railway says "project exited":

1. **Check logs**:
   ```powershell
   railway logs --service api
   railway logs --service web
   ```

2. **Common fixes**:
   - **Port binding**: Ensure your app uses `process.env.PORT`
   - **Missing start command**: Add `"start": "node dist/main.js"` to package.json
   - **Missing DATABASE_URL**: Set it in Railway dashboard

3. **Check service status**:
   ```powershell
   railway status
   railway variables list
   ```

## 📊 Expected Results

After successful deployment:
- **API**: `https://anti-fraud-platform-api-production.up.railway.app`
- **Web**: `https://anti-fraud-platform-web-production.up.railway.app`
- **API Docs**: `https://anti-fraud-platform-api-production.up.railway.app/docs`

## 🎉 Next Steps

1. **Apply the database schema** using Railway's database console
2. **Test all endpoints** with the verification script
3. **Configure custom domains** if needed
4. **Set up monitoring** and alerts

Your Anti-Fraud Platform will be live on Railway! 🚀
