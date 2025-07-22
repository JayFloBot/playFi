# Trading Research Platform

A comprehensive web-based trading research platform that allows users to analyze stocks, options, futures, and crypto assets using technical analysis and machine learning forecasting.

## Features

### 🎯 Core Functionality
- **Multi-Asset Support**: Stocks, crypto, futures, and options
- **Interactive Charts**: Real-time candlestick charts with technical indicators
- **Strategy Analysis**: Predefined trading strategies with backtesting
- **ML Forecasting**: Hybrid rule-based + machine learning predictions
- **News Integration**: Market news with sentiment analysis
- **Export Tools**: PDF reports, CSV data, and shareable summaries

### 📊 Technical Indicators
- Moving Averages (SMA/EMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Volume Analysis
- VWAP (Volume Weighted Average Price)
- Bollinger Bands

### 🧠 Trading Strategies
- **Equity**: Long/Short momentum and mean reversion
- **Options**: Spreads, straddles, strangles, iron condors
- **Futures**: Trend following and breakout strategies
- **Crypto**: Momentum and volatility strategies

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Recharts** for interactive charts
- **Tanstack Query** for data fetching
- **Lucide React** for icons

### Backend
- **FastAPI** (Python) for REST API
- **PostgreSQL** with TimescaleDB for time series data
- **Redis** for caching
- **Celery** for background tasks
- **yfinance** for market data
- **scikit-learn/XGBoost** for ML models

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd trading-research-platform
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

1. **Backend Setup**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend Setup**:
```bash
npm install
npm run dev
```

3. **Database Setup** (PostgreSQL and Redis required):
```bash
# Update DATABASE_URL and REDIS_URL in .env
cp .env.example .env
```

## Usage Guide

### 1. Asset Selection
- Use the search bar to find stocks, crypto, futures, or options
- Select from popular assets or search by symbol/name
- View real-time market data and key metrics

### 2. Chart Analysis
- Choose timeframes: 1h, 4h, 1d, 1w, 1M, 3M, 6M, 1Y, 3Y, 5Y, YTD
- Toggle technical indicators on/off
- View entry and exit points overlaid on charts

### 3. Strategy Selection
- Browse available strategies by asset type
- Filter by risk level (Low/Medium/High)
- View strategy details including success rates and capital requirements

### 4. Forecast Generation
- Select an asset and strategy
- Click "Generate Forecast" for ML-powered analysis
- Review confidence scores, expected returns, and risk metrics
- Get specific entry/exit points and reasoning

### 5. Backtesting
- Test strategies on historical data
- Configure parameters: capital, commission, slippage
- Analyze performance metrics: Sharpe ratio, drawdown, win rate

### 6. Export Results
- Generate PDF reports for sharing
- Export data to CSV for further analysis
- Create shareable text summaries

## API Documentation

The backend provides a comprehensive REST API. Access the interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Assets
- `GET /api/assets/search` - Search for assets
- `GET /api/assets/{symbol}` - Get asset information
- `GET /api/assets/{symbol}/market-data` - Get current market data

#### Prices
- `GET /api/prices/{symbol}/historical` - Historical price data
- `GET /api/prices/{symbol}/realtime` - Real-time price data
- `GET /api/prices/{symbol}/indicators` - Technical indicators

#### Strategies
- `GET /api/strategies` - List available strategies
- `GET /api/strategies/{id}` - Get strategy details

#### Forecasting
- `POST /api/forecast` - Generate single forecast
- `POST /api/forecast/batch` - Generate multiple forecasts

#### Backtesting
- `POST /api/backtest` - Run strategy backtest
- `GET /api/backtest/history/{symbol}` - Backtest history

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/trading_research

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (Optional)
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key

# Security
SECRET_KEY=your-secret-key
```

### Data Sources
The platform uses multiple data sources:
- **yfinance**: Primary source for stocks, crypto, and futures
- **Alpha Vantage**: Enhanced data feeds (optional)
- **Finnhub**: News and fundamental data (optional)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   PostgreSQL    │
│   (Port 3000)   │◄──►│   Backend       │◄──►│   Database      │
│                 │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Port 6379)   │
                       └─────────────────┘
```

## Development

### Project Structure
```
trading-research-platform/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── services/          # API services
│   ├── types/             # TypeScript types
│   └── lib/               # Utilities
├── backend/               # Python backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   ├── models/        # Data models
│   │   └── core/          # Configuration
│   └── requirements.txt
├── docker-compose.yml     # Docker services
└── README.md
```

### Adding New Features

1. **New Strategy**: Add to `backend/app/services/strategy_service.py`
2. **New Indicator**: Extend `backend/app/services/market_data.py`
3. **New UI Component**: Create in `src/components/`
4. **New API Endpoint**: Add to `backend/app/api/routes/`

## Deployment

### Production Deployment

1. **Environment Setup**:
```bash
# Set production environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://...
export SECRET_KEY=...
```

2. **Build and Deploy**:
```bash
# Build frontend
npm run build

# Deploy using Docker
docker-compose -f docker-compose.prod.yml up -d
```

3. **Database Migration**:
```bash
# Run migrations
docker-compose exec backend alembic upgrade head
```

### Scaling Considerations
- Use Redis Cluster for distributed caching
- Implement database read replicas for high load
- Add Celery workers for background processing
- Use CDN for static assets

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section below

## Troubleshooting

### Common Issues

1. **Backend won't start**:
   - Check database connection
   - Verify Python dependencies
   - Review environment variables

2. **Frontend build fails**:
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify TypeScript configuration

3. **Data not loading**:
   - Check API endpoints are accessible
   - Verify CORS configuration
   - Review browser network tab for errors

4. **Charts not displaying**:
   - Ensure Recharts is properly installed
   - Check data format compatibility
   - Verify chart component props

### Performance Tips

- Use Redis caching for frequently accessed data
- Implement pagination for large datasets
- Optimize database queries with proper indexing
- Use React.memo for expensive components

---

Built with ❤️ for traders and analysts who want better research tools.
