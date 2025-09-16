# Anti-Fraud Platform - Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
3. **EAS Account**: Sign up at [expo.dev](https://expo.dev)
4. **Clerk Account**: Sign up at [clerk.com](https://clerk.com)

## Environment Setup

1. Copy environment template:
```bash
cp env.example .env
```

2. Update `.env` with your actual values:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon key
- `SUPABASE_DB_URL`: Your Supabase database URL
- `CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
- `CLERK_SECRET_KEY`: Your Clerk secret key
- `VERCEL_TOKEN`: Your Vercel API token
- `VERCEL_ORG_ID`: Your Vercel organization ID
- `VERCEL_PROJECT_ID`: Your Vercel project ID
- `EXPO_TOKEN`: Your Expo access token

## Database Setup

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note down the URL and keys

2. **Apply Database Schema**:
```bash
# Using Supabase CLI
supabase db push

# Or manually via Supabase Dashboard
# Copy and paste the contents of infra/schema.sql
```

3. **Verify RLS Policies**:
```bash
# Test RLS is working
supabase db reset
```

## Web Deployment (Vercel)

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Deploy Web App**:
```bash
cd web
vercel --prod
```

3. **Set Environment Variables in Vercel**:
   - Go to Vercel Dashboard → Project Settings → Environment Variables
   - Add all variables from `.env`

## API Deployment (Vercel Functions)

1. **Deploy API**:
```bash
cd api
vercel --prod
```

2. **Set Environment Variables in Vercel**:
   - Add all API-specific variables

## Mobile Deployment (EAS)

1. **Install EAS CLI**:
```bash
npm install -g @expo/eas-cli
```

2. **Login to EAS**:
```bash
eas login
```

3. **Configure EAS**:
```bash
cd mobile
eas build:configure
```

4. **Build for Development**:
```bash
eas build --platform all --profile development
```

5. **Build for Production**:
```bash
eas build --platform all --profile production
```

6. **Submit to App Stores**:
```bash
eas submit --platform all
```

## Verification

1. **Web App**: Visit your Vercel URL
2. **API**: Test endpoints at `https://your-api.vercel.app/health`
3. **Mobile**: Install development build on device

## Rollback Commands

### Database Rollback
```bash
# Apply rollback schema
psql $SUPABASE_DB_URL -f infra/rollback.sql
```

### Vercel Rollback
```bash
# Rollback to previous deployment
vercel rollback

# Or rollback to specific deployment
vercel rollback <deployment-url>
```

### EAS Rollback
```bash
# Build previous version
eas build --platform all --profile production --non-interactive
```

## Monitoring

1. **Vercel Analytics**: Monitor web performance
2. **Supabase Dashboard**: Monitor database performance
3. **EAS Dashboard**: Monitor mobile builds
4. **Sentry**: Monitor errors and performance

## Security Checklist

- [ ] RLS policies are enabled and tested
- [ ] Environment variables are properly set
- [ ] API endpoints are protected
- [ ] CORS is properly configured
- [ ] Rate limiting is implemented
- [ ] Secrets are not exposed in logs

## Performance Targets

- **API p99.9**: < 400ms
- **Web LCP**: < 2.5s
- **Mobile cold start**: < 3s

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check `SUPABASE_DB_URL` format
   - Verify database is running
   - Check RLS policies

2. **Vercel Deployment Failed**:
   - Check build logs
   - Verify environment variables
   - Check function size limits

3. **EAS Build Failed**:
   - Check `eas.json` configuration
   - Verify app signing certificates
   - Check for missing dependencies

### Support

- **Documentation**: Check individual service docs
- **Community**: GitHub Issues
- **Enterprise**: Contact support team
