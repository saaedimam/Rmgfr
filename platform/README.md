# Anti-Fraud Platform

A comprehensive fraud detection and prevention platform that protects businesses from financial losses through real-time transaction monitoring, risk scoring, and automated decision-making.

## 🏗️ Architecture

- **Web**: Next.js 14 + TypeScript (App Router/RSC) on Vercel
- **API**: FastAPI (Python 3.12) on Railway
- **Database**: Postgres (Supabase) with RLS
- **Cache**: Redis (optional)
- **Auth**: Clerk
- **Mobile**: Expo + React Native (EAS)
- **CI/CD**: GitHub Actions
- **Observability**: Sentry + basic OpenTelemetry

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.12+
- Docker & Docker Compose
- pnpm (recommended)

### Development Setup

1. **Install dependencies:**
```bash
pnpm install
cd api && pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Copy environment files
cp web/.env.example web/.env.local
cp api/.env.example api/.env
cp mobile/.env.example mobile/.env

# Edit the files with your actual values
```

3. **Start the development environment:**
```bash
# Option 1: Using Docker Compose (recommended)
pnpm run docker:up

# Option 2: Manual setup
pnpm run dev
```

4. **Set up the database:**
```bash
pnpm run setup:db
```

### Access Points

- **Web App**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Mobile**: Use Expo Go app with the QR code from `pnpm run dev:mobile`

## 📱 Features

### Core Functionality
- ✅ Real-time transaction scoring
- ✅ Fraud case management
- ✅ Policy configuration
- ✅ Analytics dashboard
- ✅ REST API for integration
- ✅ Mobile app with push notifications

### Fraud Detection Rules
- ✅ Rate limiting (IP, user, device)
- ✅ Velocity checks (events per time period)
- ✅ Device fingerprinting
- ✅ Custom rule engine
- ✅ Risk scoring (0-1 scale)

### Dashboard Features
- ✅ Real-time event monitoring
- ✅ Decision timeline
- ✅ Case queue management
- ✅ Rule performance analytics
- ✅ Risk score visualization

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Run specific test suites
pnpm run test:unit    # API unit tests
pnpm run test:e2e     # End-to-end tests
pnpm run test:e2e:ui  # E2E tests with UI

# Run tests in watch mode
cd api && python -m pytest tests/ -v --cov=src
```

## 🚀 Deployment

### Web (Vercel)
```bash
pnpm run deploy:web
```

### API (Railway)
```bash
pnpm run deploy:api
```

### Mobile (EAS)
```bash
cd mobile
pnpm run build:android  # or build:ios
pnpm run submit:android # or submit:ios
```

## 📊 API Endpoints

### Events
- `POST /v1/events` - Create transaction event
- `GET /v1/events` - List events with pagination
- `GET /v1/events/{id}` - Get specific event

### Decisions
- `POST /v1/decisions` - Create fraud decision
- `GET /v1/decisions` - List decisions with pagination
- `GET /v1/decisions/{id}` - Get specific decision

### Cases
- `GET /v1/cases` - List fraud cases
- `GET /v1/cases/{id}` - Get specific case
- `PATCH /v1/cases/{id}` - Update case
- `POST /v1/cases` - Create new case

### Health
- `GET /health` - Health check endpoint

## 🔧 Development

### Code Quality
```bash
# Lint all code
pnpm run lint

# Format all code
pnpm run format

# Type checking
cd web && pnpm run type-check
```

### Database Management
```bash
# Run migrations
cd api && alembic upgrade head

# Create new migration
cd api && alembic revision --autogenerate -m "description"

# Reset database
pnpm run setup:db
```

## 📱 Mobile Development

```bash
# Start Expo development server
cd mobile
pnpm start

# Run on specific platform
pnpm run android  # or ios, web

# Build for production
pnpm run build:android
pnpm run build:ios
```

## 🔒 Security

- Row Level Security (RLS) enabled on all tables
- API key authentication
- Input validation with Pydantic
- CORS configuration
- Rate limiting
- Secure headers

## 📈 Monitoring

- Sentry integration for error tracking
- Basic OpenTelemetry for observability
- Health check endpoints
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@antifraud.com or join our Slack channel.

---

**Built with ❤️ by the Anti-Fraud Solutions Inc team**
