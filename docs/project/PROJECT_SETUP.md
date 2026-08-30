# AdventureWorks Analytics Platform — Project Setup

## Project Structure

```
AdventureWorks Analytics Platform/
├── src/                      # Source code for ETL, connectors, and utilities
│   ├── connectors/          # Database connection modules
│   ├── bronze/              # Bronze layer (raw data ingestion)
│   ├── silver/              # Silver layer (transformation & cleaning)
│   ├── gold/                # Gold layer (analytics & serving)
│   └── utils/               # Utility functions and helpers
├── tests/                   # Unit and integration tests
├── docs/                    # Documentation and specifications
├── notebooks/               # Jupyter notebooks for exploration & analysis
├── scripts/                 # Utility scripts and maintenance
│   └── init-db.sql         # PostgreSQL initialization script
├── config/                  # Configuration files and constants
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker Compose for PostgreSQL
├── README.md               # Project overview
└── Phase_Checklist.md      # Task tracking
```

## Getting Started

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 4. Start PostgreSQL
```bash
docker-compose up -d
```

### 5. Verify Connectivity
- Test SQL Server connection
- Test PostgreSQL connection
- Run initial profiling queries

## Key Files

- **requirements.txt**: All Python dependencies
- **docker-compose.yml**: PostgreSQL container configuration
- **.env.example**: Template for environment variables
- **.gitignore**: Git ignore patterns
- **Phase_Checklist.md**: Actionable task checklist

## Next Steps

1. Complete Phase 0 tasks:
   - Configure .env with actual credentials
   - Start PostgreSQL via Docker
   - Test SQL Server connectivity
   - Test PostgreSQL connectivity
   - Create schemas (bronze, silver, gold)

2. Move to Phase 1: Data Discovery & Profiling
