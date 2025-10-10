# SubmitEZ Architecture

This document describes the system architecture, design patterns, and technical decisions for the SubmitEZ MVP.

---

## 🏛️ Architecture Overview

SubmitEZ follows a **layered architecture** with clear separation of concerns and SOLID principles.

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Upload UI   │  │  Review UI   │  │ Download UI  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│            │              │                  │           │
│            └──────────────┴──────────────────┘           │
│                          │                               │
│                    API Client Layer                      │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────┴─────────────────────────────┐
│                  Backend (Flask API)                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │              API Layer                          │    │
│  │  • Routes (submission_routes.py)                │    │
│  │  • Middleware (error handling, validation)      │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Service Layer (Core)                  │    │
│  │  • SubmissionService (orchestrator)             │    │
│  │  • ExtractionService                            │    │
│  │  • ValidationService                            │    │
│  │  • GenerationService                            │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │          Domain Layer                           │    │
│  │  • Models (Applicant, Property, Coverage)       │    │
│  │  • Schemas (Pydantic validation)                │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │       Infrastructure Layer                      │    │
│  │  • Database (Supabase/PostgreSQL)               │    │
│  │  • Storage (Supabase Storage)                   │    │
│  │  • AI (OpenAI GPT-4)                            │    │
│  │  • PDF (ReportLab, fillpdf)                     │    │
│  │  • Processors (PDF, Excel, ACORD)               │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔷 Layer Responsibilities

### 1. API Layer (`app/api/`)
**Responsibility:** HTTP interface and request/response handling

- **Routes** - REST endpoint definitions
- **Middleware** - Cross-cutting concerns (error handling, validation, logging)
- **Request/Response Models** - HTTP-specific DTOs

**Key Files:**
- `routes/submission_routes.py` - Submission CRUD and workflow endpoints
- `middleware/error_handler.py` - Global exception handling
- `middleware/request_validator.py` - File and request validation

---

### 2. Service Layer (`app/core/services/`)
**Responsibility:** Business logic orchestration

Services coordinate between domain models, processors, and infrastructure:

- **SubmissionService** - Main orchestrator for the submission workflow
- **ExtractionService** - Coordinates document processing and AI extraction
- **ValidationService** - Applies business rules and validates data
- **GenerationService** - Orchestrates PDF generation

**Design Pattern:** Service Layer pattern - encapsulates business logic, orchestrates operations

---

### 3. Domain Layer (`app/domain/`)
**Responsibility:** Core business entities and rules

#### Models (`domain/models/`)
Pure Python classes representing business entities:
- `Applicant` - Insured business information
- `PropertyLocation` - Physical property details
- `Coverage` - Insurance coverage specifications
- `LossHistory` - Claims history
- `Submission` - Aggregate root containing all above

#### Schemas (`domain/schemas/`)
Pydantic models for validation:
- Input validation (API requests)
- Output serialization (API responses)
- Data transfer between layers

**Design Pattern:** Domain-Driven Design (DDD) - Submission is an aggregate root

---

### 4. Infrastructure Layer (`app/infrastructure/`)
**Responsibility:** External service integration

#### Database (`infrastructure/database/`)
- **Repositories** - Data access abstraction (Repository pattern)
- **Supabase Client** - Database connection management

#### Storage (`infrastructure/storage/`)
- **Abstract Interface** - `BaseStorage`
- **Implementation** - `SupabaseStorage` for file operations

#### AI (`infrastructure/ai/`)
- **Abstract Interface** - `BaseLLM`
- **Implementation** - `OpenAIClient` for GPT-4 extraction
- **Prompts** - Template-based prompt engineering

#### PDF (`infrastructure/pdf/`)
- **Abstract Interface** - `BasePDFGenerator`
- **Implementations** - ACORD generator, Carrier generator

#### Processors (`core/processors/`)
Document processing components:
- **Abstract Base** - `BaseProcessor`
- **Implementations** - PDF, Excel, ACORD processors
- **Factory** - `ProcessorFactory` for processor selection

**Design Pattern:** Dependency Inversion - depend on abstractions, not implementations

---

## 🔄 Data Flow

### End-to-End Submission Flow

```
1. UPLOAD
   Client → API Route → SubmissionService
   ├─ Validate file types/sizes
   ├─ Upload to Supabase Storage
   └─ Create submission record in DB

2. EXTRACT
   API Route → ExtractionService
   ├─ ProcessorFactory selects appropriate processor
   ├─ Processor extracts text/tables from documents
   ├─ LLM (GPT-4) extracts structured data
   └─ Save extracted data to submission record

3. VALIDATE
   API Route → ValidationService
   ├─ Check required fields
   ├─ Validate data consistency
   ├─ Cross-field validation rules
   └─ Return validation report

4. GENERATE
   API Route → GenerationService
   ├─ Load submission data
   ├─ ACORD Generator → ACORD 125, 140 PDFs
   ├─ Carrier Generator → Custom forms
   └─ Store generated PDFs

5. DOWNLOAD
   API Route → Storage Service
   ├─ Retrieve generated PDFs
   └─ Return download URLs or file streams
```

---

## 🎨 Design Patterns

### 1. **Repository Pattern**
Abstracts data access logic from business logic.

```python
class BaseRepository(ABC):
    @abstractmethod
    def create(self, entity): pass
    
    @abstractmethod
    def get(self, id): pass
    
    @abstractmethod
    def update(self, id, data): pass

class SubmissionRepository(BaseRepository):
    # Concrete implementation using Supabase
    pass
```

**Benefits:**
- Swap database implementations easily
- Testable without real database
- Clean separation of concerns

---

### 2. **Factory Pattern**
Creates appropriate processor based on file type.

```python
class ProcessorFactory:
    @staticmethod
    def create_processor(file_type: str) -> BaseProcessor:
        if file_type == 'pdf':
            return PDFProcessor()
        elif file_type == 'xlsx':
            return ExcelProcessor()
        elif is_acord_form(file_type):
            return ACORDProcessor()
```

**Benefits:**
- Easy to add new document types
- Centralized processor creation logic
- Follows Open/Closed Principle

---

### 3. **Strategy Pattern**
Interchangeable AI providers and PDF generators.

```python
class BaseLLM(ABC):
    @abstractmethod
    def extract_data(self, text: str, schema: dict): pass

class OpenAIClient(BaseLLM):
    def extract_data(self, text: str, schema: dict):
        # OpenAI implementation
        pass

class ClaudeClient(BaseLLM):
    def extract_data(self, text: str, schema: dict):
        # Anthropic Claude implementation
        pass
```

**Benefits:**
- Swap AI providers without changing business logic
- A/B test different extraction approaches
- Cost optimization by provider

---

### 4. **Service Layer Pattern**
Encapsulates business logic and orchestration.

```python
class SubmissionService:
    def __init__(self, 
                 repository: SubmissionRepository,
                 storage: BaseStorage,
                 extraction_service: ExtractionService):
        self.repository = repository
        self.storage = storage
        self.extraction_service = extraction_service
    
    def create_submission(self, files):
        # Orchestrate upload workflow
        pass
```

**Benefits:**
- Business logic independent of HTTP layer
- Reusable across different interfaces (API, CLI)
- Easier to test

---

### 5. **Aggregate Root (DDD)**
Submission is the main aggregate containing related entities.

```python
class Submission:
    def __init__(self):
        self.applicant: Applicant
        self.locations: List[PropertyLocation]
        self.coverage: Coverage
        self.loss_history: List[LossHistory]
        self.status: str
        self.metadata: dict
```

**Benefits:**
- Maintains consistency boundaries
- Single entry point for submission operations
- Enforces business invariants

---

## 🗄️ Database Schema

### Submissions Table

```sql
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status VARCHAR(50) NOT NULL,  -- 'uploaded', 'extracted', 'validated', 'generated'
    
    -- Submission metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Extracted data (JSONB for flexibility)
    applicant JSONB,
    locations JSONB,  -- Array of property locations
    coverage JSONB,
    loss_history JSONB,  -- Array of losses
    
    -- File references
    uploaded_files JSONB,  -- Array of file paths in storage
    generated_files JSONB,  -- Array of generated PDF paths
    
    -- Validation
    validation_errors JSONB,
    validation_warnings JSONB,
    
    -- Extraction metadata
    extraction_metadata JSONB,  -- confidence scores, model version, etc.
    
    CONSTRAINT valid_status CHECK (status IN ('uploaded', 'extracting', 'extracted', 'validated', 'generating', 'completed', 'error'))
);

CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_submissions_created_at ON submissions(created_at DESC);
```

**Why JSONB?**
- Flexible schema for MVP iteration
- Fast queries with GIN indexes
- Easy to add new fields without migrations
- Native PostgreSQL support in Supabase

---

## 🔐 Security Considerations

### File Upload Security
- File type validation (whitelist: PDF, Excel, Word)
- File size limits (16MB max)
- Virus scanning (future enhancement)
- Sanitized filenames

### API Security
- CORS configuration for frontend origin
- Request size limits
- Rate limiting (future enhancement)
- Input validation via Pydantic schemas

### Data Security
- Sensitive data stored in Supabase (encrypted at rest)
- Environment variables for secrets
- No hardcoded credentials
- Secure file storage with access controls

---

## 📊 Scalability Considerations

### Current MVP Design
- Synchronous processing (acceptable for MVP)
- Single server deployment
- Direct database queries

### Future Enhancements
1. **Async Processing** - Celery + Redis for long-running tasks
2. **Caching** - Redis for frequent queries
3. **Load Balancing** - Multiple API instances
4. **CDN** - Static file delivery
5. **Database** - Read replicas, connection pooling
6. **Monitoring** - Application performance monitoring (APM)

---

## 🧪 Testing Strategy

### Unit Tests
- Domain models (business logic)
- Services (mocked dependencies)
- Processors (document parsing)
- Validators (business rules)

### Integration Tests
- API endpoints (full request/response)
- Database operations (real Supabase test instance)
- File upload/download flows

### E2E Tests (Future)
- Complete submission workflow
- UI interaction testing with Playwright

---

## 🚀 Deployment Architecture

### Development
```
Local Machine
├── Backend (Flask dev server) - :5000
├── Frontend (Next.js dev) - :3000
└── Supabase Cloud (dev project)
```

### Production (Recommended)
```
┌─────────────────────────────────────┐
│         Vercel (Frontend)           │
│     https://submitez.vercel.app     │
└─────────────────────────────────────┘
                │
                │ HTTPS
                ↓
┌─────────────────────────────────────┐
│    Railway/Render (Backend API)     │
│     https://api.submitez.com        │
└─────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────┐
│      Supabase (Database + Storage)  │
└─────────────────────────────────────┘
```

---

## 📈 Performance Targets (MVP)

| Metric | Target | Notes |
|--------|--------|-------|
| Upload | < 5s | For files < 10MB |
| Extraction | < 30s | Per document (GPT-4 call) |
| Validation | < 1s | Business rules only |
| PDF Generation | < 10s | ACORD + 2 carrier forms |
| Total Workflow | < 2 min | From upload to download |

---

## 🔧 Technology Decisions

### Why Flask?
- Lightweight, flexible
- Easy to structure with blueprints
- Rich ecosystem for integrations
- Simple to deploy

### Why Supabase?
- PostgreSQL + Storage + Auth in one
- Quick setup, no infrastructure management
- Real-time capabilities (future)
- Generous free tier for MVP

### Why OpenAI GPT-4?
- Best-in-class extraction accuracy
- Structured output support (JSON mode)
- Function calling for validation
- Proven for document understanding

### Why Next.js?
- React with server-side rendering
- File-based routing
- Built-in API routes (if needed)
- Vercel deployment optimization
- TypeScript support

---

## 🎯 Design Principles Summary

1. **SOLID Principles** - Maintainable, extensible code
2. **Separation of Concerns** - Clear layer boundaries
3. **Dependency Inversion** - Abstractions over implementations
4. **Single Source of Truth** - Domain models as canonical data
5. **Fail Fast** - Early validation, clear error messages
6. **Progressive Enhancement** - Start simple, add complexity as needed

---

## 📚 Further Reading

- [Flask Best Practices](https://flask.palletsprojects.com/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)