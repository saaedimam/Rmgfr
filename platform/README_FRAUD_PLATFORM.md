# Anti-Fraud Platform

A comprehensive real-time fraud detection and prevention platform built with Next.js, FastAPI, and PostgreSQL.

## 🚀 Features

### Real-time Fraud Detection
- **Multi-factor Risk Analysis**: Velocity, device anomaly, geolocation, behavioral, and payment risk
- **Real-time Decision Making**: Allow, deny, review, or step-up authentication
- **Advanced Pattern Recognition**: Detects suspicious user agents, IP patterns, and behavioral anomalies
- **Configurable Risk Thresholds**: Customizable risk levels and decision matrices

### Web Dashboard
- **Real-time Monitoring**: Live event processing and alerts
- **Analytics & Insights**: Comprehensive fraud detection analytics
- **Event Testing**: Interactive event testing interface
- **Settings Management**: Configure fraud detection rules and thresholds

### API Services
- **RESTful API**: Complete fraud detection API with OpenAPI documentation
- **Database Integration**: PostgreSQL with connection pooling and health monitoring
- **Replay Worker**: Event reprocessing and analysis capabilities
- **Comprehensive Testing**: Full test suite with 10+ test cases

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Dashboard │    │   API Server    │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Replay Worker │
│   (Expo/RN)     │    │   (Background)  │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Lucide React
- **Backend**: FastAPI, Python 3.12, Pydantic v2
- **Database**: PostgreSQL (Supabase), asyncpg
- **Mobile**: Expo, React Native
- **Testing**: pytest, aiohttp
- **Deployment**: Vercel, Docker

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- PostgreSQL (or Supabase)
- Git

### 1. Clone and Setup
```bash
git clone <repository-url>
cd platform
```

### 2. Install Dependencies
```bash
# Install web dependencies
cd web
npm install

# Install API dependencies
cd ../api
pip install -r requirements.txt

# Install mobile dependencies
cd ../mobile
npm install
```

### 3. Configure Environment
```bash
# Copy environment files
cp api/env.example api/.env
cp web/env.example web/.env.local

# Set up database URL
export SUPABASE_DB_URL="postgresql://user:password@host:5432/database"
```

### 4. Start the Platform
```bash
# Option 1: Start everything at once
python scripts/start_platform.py

# Option 2: Start services individually
# Terminal 1: API Server
cd api && python -m uvicorn src.main:app --reload --port 8000

# Terminal 2: Web Server
cd web && npm run dev

# Terminal 3: Mobile App (optional)
cd mobile && npx expo start
```

### 5. Access the Platform
- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📊 Dashboard Features

### Real-time Monitoring
- Live event processing with real-time updates
- Event statistics and risk score analysis
- Decision tracking (allow/deny/review/step_up)
- Performance metrics and processing times

### Analytics
- Event trends over time
- Risk score distribution analysis
- Top firing rules and patterns
- Success/failure rates

### Event Testing
- Interactive event creation and testing
- Custom event data configuration
- Real-time risk assessment
- Decision result analysis

### Settings
- Risk threshold configuration
- Velocity limits and rules
- Payment-specific settings
- Device fingerprinting options
- Notification preferences

## 🔧 API Endpoints

### Events
- `POST /v2/events/` - Create and process events
- `GET /v2/events/` - List events with filtering
- `GET /v2/events/{id}` - Get specific event
- `GET /v2/events/stats/summary` - Event statistics

### Dashboard
- `GET /v1/dashboard/stats` - Dashboard statistics
- `GET /v1/dashboard/trends` - Event trends
- `GET /v1/dashboard/recent-events` - Recent events
- `GET /v1/dashboard/top-rules` - Top firing rules

### Health & Monitoring
- `GET /health` - API health check
- `GET /health/database` - Database health
- `GET /v1/replay/worker/status` - Replay worker status

## 🧪 Testing

### Run Tests
```bash
# API tests
cd api
python -m pytest tests/ -v

# Web tests
cd web
npm run test

# End-to-end tests
python scripts/test_api_endpoints.py
```

### Demo Scripts
```bash
# Real-time demo
python scripts/demo_real_time.py

# Comprehensive testing
python scripts/start_api_test.py
```

## 📈 Performance

- **API Response Time**: < 100ms for event processing
- **Database Queries**: Optimized with connection pooling
- **Real-time Updates**: 30-second refresh intervals
- **Concurrent Processing**: Supports multiple simultaneous events

## 🔒 Security

- **Input Validation**: Comprehensive data validation with Pydantic
- **SQL Injection Prevention**: Parameterized queries
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Error Handling**: Secure error responses without sensitive data

## 🚀 Deployment

### Production Setup
1. **Database**: Set up PostgreSQL or Supabase
2. **Environment**: Configure production environment variables
3. **API**: Deploy FastAPI to your preferred platform
4. **Web**: Deploy Next.js to Vercel or similar
5. **Monitoring**: Set up logging and monitoring

### Docker Support
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running
- **Component Library**: See `platform/web/components/`
- **Database Schema**: See `platform/infra/db/`
- **Test Examples**: See `platform/scripts/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
. Run the test suite
- Review the API logs
- Open an issue on GitHub

---

**Built with ❤️ for fraud prevention and security**
