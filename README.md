# AI-GAPSIM: Power Grid Weather Resiliency Tool

AI-GAPSIM (Artificial Intelligence Geospatial Atmosphere Power System Interaction Model) is a comprehensive web application for visualizing and analyzing the impact of weather on power grid infrastructure across the Western Electricity Coordinating Council (WECC) region.

## Features

- Interactive map visualization of power grid components (transmission lines, generators, substations, etc.)
- Weather heatmaps for temperature, humidity, wind speed, precipitation, and solar radiation
- Time-based analysis with date range selection and animation
- Impact calculations showing how weather affects grid components
- Balancing Authority visualization and analysis
- User authentication and authorization

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL + PostGIS (database)
- Redis (caching)
- Pandas & GeoPandas (data processing)
- JWT for authentication

### Frontend
- React with TypeScript
- Vite (build tool)
- React Router (navigation)
- Tailwind CSS (styling)
- React Leaflet (maps)
- Recharts (charts)
- Zustand (state management)

### Deployment
- Docker & Docker Compose

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/smanishs175/AI-GAPSIM.git
   cd AI-GAPSIM
   ```

2. Create environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Start the application using the provided script:
   ```bash
   ./scripts/start_app.sh
   ```
   This will start the application in development mode and initialize the database if needed.

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PgAdmin (database management): http://localhost:5050

### Production Deployment

1. Create a production environment file:
   ```bash
   cp .env.prod.example .env.prod
   ```

2. Edit the `.env.prod` file with your production settings.

3. Deploy the application using the provided script:
   ```bash
   ./scripts/deploy.sh
   ```

### Utility Scripts

The project includes several utility scripts to help with common tasks:

#### Database Management

- Initialize or reset the database:
  ```bash
  ./scripts/init_db.sh
  ```

- Backup the database and data files:
  ```bash
  ./scripts/backup.sh
  ```

- Restore from a backup:
  ```bash
  ./scripts/restore.sh backups/db_backup_YYYYMMDD_HHMMSS.sql backups/data_backup_YYYYMMDD_HHMMSS.tar.gz
  ```

#### Application Management

- Start the application:
  ```bash
  ./scripts/start_app.sh [dev|prod]
  ```

- Update the application:
  ```bash
  ./scripts/update.sh
  ```

- Monitor the application:
  ```bash
  ./scripts/monitor.sh [logs|status|stats]
  ```

- Clean up the environment:
  ```bash
  ./scripts/cleanup.sh [--all]
  ```

#### Data Management

- Generate sample data:
  ```bash
  ./scripts/generate_sample_data.sh
  ```

## Development

### Running Tests

To run the tests, use the provided script:

```bash
./scripts/run_tests.sh [backend|frontend|all]
```

This will run the tests for the specified component(s). If no component is specified, it will run all tests.

### Backend Development

1. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Development

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the Vite development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
AI-GAPSIM/
├── backend/              # FastAPI application
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   ├── tests/            # Backend tests
│   └── requirements.txt  # Python dependencies
├── frontend/             # React application
│   ├── public/           # Static assets
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client functions
│   │   ├── store/        # State management
│   │   └── utils/        # Utility functions
│   └── package.json      # Node.js dependencies
├── data/                 # Data files
└── docker-compose.yml    # Docker Compose configuration
```

## Data Sources

The application uses power grid data from the Western Electricity Coordinating Council (WECC) region, including:

- Transmission lines
- Generators
- Loads
- Substations
- Buses
- Balancing Authorities
- Weather data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Western Electricity Coordinating Council (WECC) for grid data
- National Solar Radiation Database (NSRDB) for weather data
- Energy Information Administration (EIA) for Balancing Authority data