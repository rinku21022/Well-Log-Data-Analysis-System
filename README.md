# Well-Log Data Analysis System

A full-stack web application for ingesting, visualizing, and analyzing subsurface well-log data from LAS (Log ASCII Standard) files using AI-assisted interpretation.

## Architecture

- **Backend**: Python Flask REST API
- **Frontend**: React.js with interactive visualization
- **Database**: PostgreSQL for structured data storage
- **Storage**: Amazon S3 for raw LAS file storage
- **AI**: OpenAI GPT for intelligent data interpretation
- **Visualization**: Plotly.js for interactive charts

## Features

✅ LAS file upload and parsing
✅ Amazon S3 integration for file storage
✅ PostgreSQL database for curve data
✅ Interactive depth-based visualization (zoom, pan)
✅ AI-assisted interpretation of selected depth ranges
✅ Conversational chatbot interface
✅ Secure API design with credential isolation

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- AWS Account (for S3)
- OpenAI API Key

## Quick Start

### 1. Clone and Setup Environment

```bash
cd "c:\Users\Lenovo\OneDrive\Desktop\New folder"
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt

# Create .env file with your credentials
copy .env.example .env
# Edit .env with your AWS and OpenAI credentials
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb welllog_db

# Run migrations
python manage.py db upgrade
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Run Application

Terminal 1 (Backend):
```bash
cd backend
venv\Scripts\activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

Access the application at: http://localhost:3000

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://username:password@localhost:5432/welllog_db
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=welllog-files
OPENAI_API_KEY=your_openai_key
FLASK_ENV=development
```

## API Endpoints

- `POST /api/upload` - Upload LAS file
- `GET /api/files` - List uploaded files
- `GET /api/file/{id}` - Get file details
- `GET /api/curves/{file_id}` - Get available curves
- `POST /api/visualize` - Get visualization data
- `POST /api/interpret` - AI interpretation
- `POST /api/chat` - Chatbot interface

## Database Choice Justification

**PostgreSQL** was selected because:
- Excellent support for structured time-series data
- JSONB support for flexible metadata storage
- Strong indexing for efficient depth-range queries
- ACID compliance for data integrity
- Scalability for large datasets

## Technology Stack Justification

- **Flask**: Lightweight, flexible, excellent for data APIs
- **React**: Component-based UI, rich ecosystem for charts
- **Plotly.js**: Interactive scientific visualizations
- **PostgreSQL**: Robust relational database for structured data
- **S3**: Reliable, scalable object storage

## Project Structure

```
welllog-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   ├── utils/                 # Utilities (LAS parser, S3)
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API clients
│   │   └── App.js            # Main app
│   └── package.json          # Node dependencies
└── README.md
```

## License

MIT License
