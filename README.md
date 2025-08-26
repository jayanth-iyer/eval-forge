# Eval Forge - LLM Evaluation Platform

A comprehensive web application for evaluating Large Language Models through various metrics and test suites, with support for local models (via Ollama) and future API-based model integrations.

## 🚀 Phase 1 Features (MVP) - COMPLETED

- ✅ **Modern Web Interface**: React + Vite + Tailwind CSS with responsive design
- ✅ **Ollama Integration**: Full support for local Llama models
- ✅ **Single Model Evaluation**: Complete evaluation workflow
- ✅ **Simple Accuracy Metrics**: Binary scoring with detailed breakdowns
- ✅ **Dataset Management**: CSV upload support + built-in sample dataset
- ✅ **Results Storage**: SQLite database with persistent storage
- ✅ **Error Handling**: Graceful error handling with custom error pages
- ✅ **Real-time Progress**: Live evaluation status and progress tracking

## 🛠️ Tech Stack

### Frontend
- **React 18** with Vite for lightning-fast development
- **Tailwind CSS** for modern, responsive design
- **React Router** for client-side navigation
- **Axios** for API communication
- **Lucide React** for beautiful icons

### Backend
- **FastAPI** (Python) for high-performance API development
- **SQLite** for development database (production-ready)
- **SQLAlchemy** for robust ORM and database management
- **Pydantic** for data validation and serialization
- **HTTPX** for async HTTP requests to Ollama

## 📋 Prerequisites

- **Node.js 18+** and npm
- **Python 3.8+** (tested with Python 3.13)
- **Ollama** running locally for model evaluation
- **Git** for version control

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd eval-forge
```

### 2. Frontend Setup
```bash
# Install frontend dependencies
npm install

# Start development server (runs on localhost:3000)
npm run dev
```

### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the API server (runs on localhost:8000)
python run.py
```

### 4. Ollama Setup
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Pull a model for testing
ollama pull llama3.2

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

## 📖 Usage Guide

### Adding Your First Model
1. Navigate to **Models** section
2. Click **Add Model**
3. Configure:
   - **Name**: "Llama 3.2 Local"
   - **Type**: "Ollama"
   - **Endpoint**: "http://localhost:11434"
   - **Model Name**: "llama3.2"
4. Click **Test Connection** to verify

### Creating an Evaluation
1. Go to **Evaluations** section
2. Click **New Evaluation**
3. Choose your options:
   - **Dataset**: Upload CSV or use sample dataset (10 questions)
   - **Model**: Select your configured model
   - **Parameters**: Adjust temperature, max tokens, top_p
4. Click **Create Evaluation**

### Running Evaluations
1. Find your evaluation in the list
2. Click the **Play** button to start
3. Monitor progress in real-time
4. View results when completed

### Analyzing Results
1. Navigate to **Results** section
2. Click **View Results** for detailed analysis
3. Filter questions by correct/incorrect
4. Review individual question responses

## 📁 Project Structure

```
eval-forge/
├── src/                          # React frontend source
│   ├── components/
│   │   └── Layout.jsx           # Main layout component
│   ├── pages/
│   │   ├── Dashboard.jsx        # Main dashboard
│   │   ├── Models.jsx           # Model management
│   │   ├── Evaluations.jsx     # Evaluation creation/management
│   │   ├── Results.jsx          # Results viewing
│   │   └── ErrorPage.jsx       # Error handling
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # React entry point
│   └── index.css               # Tailwind CSS imports
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app and routes
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── schemas.py          # Pydantic validation schemas
│   │   └── database.py         # Database configuration
│   ├── venv/                   # Python virtual environment
│   ├── requirements.txt        # Python dependencies
│   └── run.py                  # Server startup script
├── proj-docs/                  # Project documentation
│   ├── features.md            # Detailed feature specifications
│   ├── game-plan.md           # Project roadmap
│   └── limitations.md         # Known limitations
├── node_modules/              # Node.js dependencies
├── package.json               # Frontend dependencies
├── package-lock.json          # Dependency lock file
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
├── index.html                # HTML entry point
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔌 API Endpoints

### Models
- `GET /api/models` - List all configured models
- `POST /api/models` - Add new model configuration
- `DELETE /api/models/{id}` - Remove model
- `GET /api/models/{id}/test` - Test model connection

### Evaluations
- `GET /api/evaluations` - List all evaluations
- `POST /api/evaluations` - Create new evaluation (with file upload)
- `POST /api/evaluations/{id}/run` - Execute evaluation

### Results
- `GET /api/results` - List completed evaluation results
- `GET /api/results/{id}` - Get detailed evaluation results
- `DELETE /api/results/{id}` - Delete evaluation and results

## 📊 Sample Dataset

The application includes a built-in sample dataset with 10 questions covering:
- **Geography**: World capitals
- **Mathematics**: Basic arithmetic
- **Literature**: Famous authors
- **Science**: Planets, chemistry
- **History**: Historical dates

## ⚠️ Known Limitations (Phase 1)

### Evaluation Limitations
- **Simple Binary Scoring**: Only Correct/Incorrect classification
- **Basic String Matching**: No semantic similarity understanding
- **Ollama-Only Support**: No cloud API integrations yet
- **Single Model Evaluation**: No comparative analysis

### Technical Limitations
- **Local Storage Only**: SQLite database (no cloud backup)
- **No User Authentication**: Single-user system
- **Basic Progress Tracking**: Simple progress indicators
- **Limited Error Analysis**: Basic error reporting

See `proj-docs/limitations.md` for comprehensive limitations and mitigation strategies.

## 🛣️ Development Roadmap

### Phase 2: Multi-Model Support (Weeks 5-8)
- Multiple model configurations and comparisons
- API integrations (OpenAI, Anthropic, Google)
- Basic visualization improvements
- Evaluation templates and presets

### Phase 3: Advanced Features (Weeks 9-12)
- Advanced metrics (BLEU, ROUGE, semantic similarity)
- Sophisticated error analysis and categorization
- Export capabilities (CSV, PDF, JSON)
- Advanced visualization and analytics

### Phase 4: Production Ready (Weeks 13-16)
- User authentication and multi-tenancy
- Cloud storage and backup options
- Performance optimizations
- Production deployment configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check that Ollama is running on `localhost:11434`
2. Verify both frontend and backend servers are running
3. Review the browser console for error messages
4. Check the backend logs for API errors

For additional help, refer to the project documentation in `proj-docs/`.
