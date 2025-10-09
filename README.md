# SubmitEZ MVP

**Commercial Insurance Submission Automation Platform**

SubmitEZ automates the tedious process of preparing commercial insurance submissions. Brokers upload documents (ACORD forms, Excel schedules, PDFs), and the system extracts data, validates it, and generates carrier-ready forms in minutes instead of hours.

---

## 🎯 Problem

Commercial insurance brokers spend **10-15 hours per week** manually retyping data from scattered documents into multiple carrier systems. This creates:
- Bottlenecks in submission processing
- Frequent data entry errors
- Delayed quotes and renewals
- Limited account capacity per broker

## 💡 Solution

**SubmitEZ** automates submission preparation:
1. **Upload** - Drop any submission files (ACORD, Excel, PDF)
2. **Extract** - AI extracts structured data automatically
3. **Review** - Broker validates and corrects in clean interface
4. **Generate** - System creates carrier-ready ACORD and custom forms
5. **Download** - Complete, validated submission package ready to send

## 🚀 Value Proposition

| Stakeholder | Pain Point | Value Delivered |
|-------------|------------|-----------------|
| Broker | Hours retyping data | **80% time reduction** |
| Account Manager | Multiple template entry | Single upload → all forms filled |
| Agency Owner | Low throughput | Higher submission capacity |
| Carrier Underwriter | Incomplete submissions | Clean, validated data |

**ROI:** Save ~10 hours/week per broker, reduce errors, faster turnaround.

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.11+ / Flask
- Supabase (PostgreSQL + Storage)
- OpenAI GPT-4 (data extraction)
- ReportLab (PDF generation)

**Frontend:**
- Next.js 14 (React)
- TypeScript
- Tailwind CSS + shadcn/ui
- Zustand (state management)

### Design Principles

Built following **SOLID principles** for maintainability and extensibility:
- **Single Responsibility** - Services handle one concern
- **Open/Closed** - Extensible via abstract processors
- **Liskov Substitution** - Swappable implementations (OpenAI ↔ Claude)
- **Interface Segregation** - Minimal, focused interfaces
- **Dependency Inversion** - Depend on abstractions, not concretions

---

## 📂 Project Structure

```
submitez-mvp/
├── backend/              # Python/Flask API
│   ├── app/
│   │   ├── api/         # Routes & middleware
│   │   ├── core/        # Services & processors
│   │   ├── domain/      # Models & schemas
│   │   ├── infrastructure/  # Database, storage, AI, PDF
│   │   └── utils/       # Utilities
│   ├── tests/
│   └── migrations/
├── frontend/            # Next.js UI
│   └── src/
│       ├── app/         # App router pages
│       ├── components/  # React components
│       ├── lib/         # API client & utils
│       ├── hooks/       # Custom hooks
│       └── types/       # TypeScript types
└── docs/               # Documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
python run.py
```

Backend will run at: `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with backend API URL

# Run development server
npm run dev
```

Frontend will run at: `http://localhost:3000`

---

## 📖 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and patterns
- **[Setup Guide](docs/SETUP.md)** - Detailed setup instructions
- **[API Reference](docs/API.md)** - API endpoints and examples

---

## 🔄 Workflow

### 1. Upload Documents
```
POST /api/submissions/upload
```
Upload ACORD forms, Excel schedules, loss runs, or any submission documents.

### 2. Extract Data
```
POST /api/submissions/{id}/extract
```
AI extracts structured data (applicant, properties, coverage, losses).

### 3. Review & Validate
```
GET /api/submissions/{id}
PATCH /api/submissions/{id}
POST /api/submissions/{id}/validate
```
Review extracted data, make corrections, validate completeness.

### 4. Generate Forms
```
POST /api/submissions/{id}/generate
```
Generate ACORD 125, 140, and carrier-specific PDFs.

### 5. Download Package
```
GET /api/submissions/{id}/download
```
Download complete submission package ready for carrier submission.

---

## 🎯 MVP Features

### ✅ Core Features
- Multi-format document upload (PDF, Excel, Word)
- AI-powered data extraction (GPT-4)
- Intelligent field mapping for ACORD forms
- Interactive data review and correction
- Business rules validation
- ACORD 125 & 140 PDF generation
- Carrier-specific form generation
- Complete submission package download

### 🚧 Post-MVP (Future)
- User authentication & multi-tenancy
- Additional ACORD forms (126, 130, etc.)
- More lines of business (GL, Auto, Cyber, WC)
- AMS system integration (Applied Epic, AMS360)
- Advanced analytics dashboard
- Email delivery to carriers
- OCR for scanned documents

---

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
flake8 app/
black app/

# Frontend linting
npm run lint
```

---

## 📊 API Health Check

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "SubmitEZ API",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```


---

## 📝 License

Proprietary - All rights reserved

---

## 📧 Support

For questions or issues, please refer to the documentation or contact the development team.

---

**Built with ❤️ for insurance brokers who deserve better tools.**