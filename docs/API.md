# SubmitEZ API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:5000`  
**API Prefix:** `/api`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Error Responses](#error-responses)
3. [Health Endpoints](#health-endpoints)
4. [Submission Endpoints](#submission-endpoints)
5. [Workflow](#workflow)
6. [Examples](#examples)

---

## Authentication

Currently, the MVP does not require authentication. Future versions will implement API key or OAuth2 authentication.

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "status_code": 400,
  "path": "/api/submissions/123",
  "method": "POST"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `413` - Request Entity Too Large
- `415` - Unsupported Media Type
- `422` - Unprocessable Entity
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Health Endpoints

### GET /health

Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "SubmitEZ",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### GET /health/detailed

Detailed health check with component status.

**Response:**
```json
{
  "status": "healthy",
  "service": "SubmitEZ",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z",
  "components": {
    "database": { "status": "healthy" },
    "storage": { "status": "healthy" },
    "processors": { "status": "healthy" },
    "extraction_service": { "status": "healthy" },
    "validation_service": { "status": "healthy" },
    "generation_service": { "status": "healthy" }
  }
}
```

### GET /health/ready

Readiness check for container orchestration.

### GET /health/live

Liveness check for container orchestration.

### GET /health/info

Service information and capabilities.

---

## Submission Endpoints

### POST /api/submissions

Create a new submission.

**Request Body (optional):**
```json
{
  "broker_name": "John Smith",
  "broker_email": "john@agency.com",
  "carrier_name": "Hartford",
  "notes": "Rush submission for renewal"
}
```

**Response (201):**
```json
{
  "message": "Submission created successfully",
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "draft",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### GET /api/submissions

List submissions with optional filtering.

**Query Parameters:**
- `status` (optional) - Filter by status: `draft`, `uploaded`, `extracted`, `validated`, `completed`
- `limit` (optional, default: 50, max: 100) - Number of results
- `offset` (optional, default: 0) - Pagination offset

**Example:**
```
GET /api/submissions?status=completed&limit=20
```

**Response (200):**
```json
{
  "submissions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "applicant_name": "ABC Company",
      "total_locations": 3,
      "total_tiv": 5000000,
      "completeness": 95,
      "is_valid": true,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "status_filter": "completed"
}
```

---

### GET /api/submissions/{submission_id}

Get submission details.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "extracted",
  "applicant": {
    "business_name": "ABC Company",
    "fein": "12-3456789",
    "mailing_city": "New York",
    "mailing_state": "NY"
  },
  "locations": [
    {
      "location_number": "1",
      "address_line1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "building_value": 2000000,
      "total_insured_value": 3000000
    }
  ],
  "coverage": {
    "policy_type": "Property",
    "effective_date": "2025-01-01",
    "building_limit": 5000000
  },
  "created_at": "2025-01-15T10:30:00Z",
  "is_valid": false,
  "validation_errors": []
}
```

---

### PATCH /api/submissions/{submission_id}

Update submission data.

**Request Body:**
```json
{
  "applicant": {
    "business_name": "ABC Company Inc",
    "email": "contact@abc.com"
  },
  "notes": "Updated contact information"
}
```

**Response (200):**
```json
{
  "message": "Submission updated successfully",
  "submission": { ... }
}
```

---

### DELETE /api/submissions/{submission_id}

Delete submission and all associated files.

**Response (200):**
```json
{
  "message": "Submission deleted successfully",
  "submission_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### POST /api/submissions/{submission_id}/upload

Upload files for submission.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `files` (array, max 10 files)
- Supported formats: PDF, XLSX, XLS, DOCX, DOC
- Max file size: 16MB per file

**Response (200):**
```json
{
  "message": "Uploaded 3 of 3 files",
  "result": {
    "submission_id": "550e8400-e29b-41d4-a716-446655440000",
    "total_files": 3,
    "successful_uploads": 3,
    "failed_uploads": 0,
    "uploaded_files": [
      {
        "filename": "acord_125_20250115_123456.pdf",
        "original_filename": "acord_125.pdf",
        "size_bytes": 245678,
        "url": "https://storage.example.com/..."
      }
    ]
  }
}
```

---

### POST /api/submissions/{submission_id}/extract

Extract data from uploaded files using AI.

**Response (200):**
```json
{
  "message": "Data extraction completed",
  "result": {
    "extraction_id": "ext_12345",
    "status": "completed",
    "overall_confidence": 0.87,
    "extracted_data": {
      "applicant": {
        "business_name": "ABC Company",
        "fein": "12-3456789",
        "confidence": 0.92
      },
      "locations": [...],
      "coverage": {...}
    },
    "duration_seconds": 12.5
  }
}
```

---

### POST /api/submissions/{submission_id}/validate

Validate submission data against business rules.

**Request Body (optional):**
```json
{
  "strict_mode": false
}
```

**Response (200):**
```json
{
  "message": "Validation completed",
  "result": {
    "validation_id": "val_12345",
    "is_valid": true,
    "is_complete": true,
    "completeness_percentage": 95,
    "total_errors": 0,
    "total_warnings": 2,
    "blocking_errors": 0,
    "errors": [],
    "warnings": [
      {
        "field_path": "applicant.naics_code",
        "severity": "warning",
        "category": "required_field",
        "message": "NAICS code is recommended"
      }
    ],
    "can_proceed_to_generation": true
  }
}
```

---

### POST /api/submissions/{submission_id}/generate

Generate ACORD and carrier forms.

**Request Body (optional):**
```json
{
  "forms": ["125", "140"],
  "carrier_name": "Hartford"
}
```

**Response (200):**
```json
{
  "message": "Form generation completed",
  "result": {
    "generation_id": "gen_12345",
    "status": "completed",
    "successful_forms": 3,
    "generated_files": [
      {
        "form_type": "ACORD 125",
        "filename": "ACORD_125_20250115.pdf",
        "url": "https://storage.example.com/...",
        "size_bytes": 156789
      },
      {
        "form_type": "ACORD 140",
        "filename": "ACORD_140_20250115.pdf",
        "url": "https://storage.example.com/..."
      },
      {
        "form_type": "Hartford Application",
        "filename": "Hartford_Application_20250115.pdf",
        "url": "https://storage.example.com/..."
      }
    ]
  }
}
```

---

### GET /api/submissions/{submission_id}/download

Get download package with all generated files.

**Response (200):**
```json
{
  "message": "Download package ready",
  "package": {
    "submission_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "applicant_name": "ABC Company",
    "total_files": 3,
    "files": [
      {
        "form_type": "ACORD 125",
        "filename": "ACORD_125_20250115.pdf",
        "url": "https://storage.example.com/...",
        "size_bytes": 156789
      }
    ],
    "completed_at": "2025-01-15T10:45:00Z"
  }
}
```

---

### POST /api/submissions/{submission_id}/process

Execute complete workflow (extract → validate → generate).

**Request Body (optional):**
```json
{
  "skip_validation": false
}
```

**Response (200):**
```json
{
  "message": "Workflow completed",
  "result": {
    "submission_id": "550e8400-e29b-41d4-a716-446655440000",
    "overall_status": "completed",
    "steps": {
      "extraction": {
        "status": "completed",
        "confidence": 0.87
      },
      "validation": {
        "status": "completed",
        "is_valid": true,
        "errors": 0
      },
      "generation": {
        "status": "completed",
        "files_generated": 3
      }
    }
  }
}
```

---

### GET /api/submissions/{submission_id}/summary

Get submission summary.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "applicant_name": "ABC Company",
  "total_locations": 3,
  "total_losses": 2,
  "total_tiv": 5000000,
  "completeness": 95,
  "is_valid": true,
  "validation_errors_count": 0,
  "validation_warnings_count": 2,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:45:00Z"
}
```

---

### GET /api/submissions/statistics

Get submission statistics.

**Response (200):**
```json
{
  "statistics": {
    "total": 150,
    "by_status": {
      "draft": 10,
      "uploaded": 5,
      "extracted": 8,
      "validated": 12,
      "completed": 115
    }
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Workflow

### Complete Submission Workflow

1. **Create Submission**
   ```bash
   POST /api/submissions
   ```

2. **Upload Files**
   ```bash
   POST /api/submissions/{id}/upload
   ```

3. **Extract Data** (AI-powered)
   ```bash
   POST /api/submissions/{id}/extract
   ```

4. **Review & Edit** (optional)
   ```bash
   PATCH /api/submissions/{id}
   ```

5. **Validate Data**
   ```bash
   POST /api/submissions/{id}/validate
   ```

6. **Generate Forms**
   ```bash
   POST /api/submissions/{id}/generate
   ```

7. **Download Package**
   ```bash
   GET /api/submissions/{id}/download
   ```

### Automated Workflow

Use the `/process` endpoint for automated workflow:

```bash
POST /api/submissions/{id}/process
```

This executes steps 3-6 automatically.

---

## Examples

### Example 1: Quick Submission

```bash
# 1. Create submission
curl -X POST http://localhost:5000/api/submissions \
  -H "Content-Type: application/json" \
  -d '{"broker_name": "John Smith", "carrier_name": "Hartford"}'

# Response: {"submission_id": "abc123", ...}

# 2. Upload files
curl -X POST http://localhost:5000/api/submissions/abc123/upload \
  -F "files=@acord_125.pdf" \
  -F "files=@schedule.xlsx"

# 3. Run automated workflow
curl -X POST http://localhost:5000/api/submissions/abc123/process

# 4. Download results
curl http://localhost:5000/api/submissions/abc123/download
```

### Example 2: Manual Review Workflow

```bash
# 1. Create and upload
curl -X POST http://localhost:5000/api/submissions
curl -X POST http://localhost:5000/api/submissions/abc123/upload -F "files=@doc.pdf"

# 2. Extract data
curl -X POST http://localhost:5000/api/submissions/abc123/extract

# 3. Get extracted data
curl http://localhost:5000/api/submissions/abc123

# 4. Edit/correct data
curl -X PATCH http://localhost:5000/api/submissions/abc123 \
  -H "Content-Type: application/json" \
  -d '{"applicant": {"email": "corrected@email.com"}}'

# 5. Validate
curl -X POST http://localhost:5000/api/submissions/abc123/validate

# 6. Generate forms
curl -X POST http://localhost:5000/api/submissions/abc123/generate \
  -H "Content-Type: application/json" \
  -d '{"forms": ["125", "140"]}'

# 7. Download
curl http://localhost:5000/api/submissions/abc123/download
```

### Example 3: Filter Submissions

```bash
# Get all completed submissions
curl "http://localhost:5000/api/submissions?status=completed&limit=50"

# Get recent submissions
curl "http://localhost:5000/api/submissions?limit=10"
```

---

## Rate Limits

Currently no rate limits in MVP. Production will implement:
- 100 requests/minute per IP
- 1000 requests/hour per API key

---

## Support

For issues or questions:
- GitHub Issues: [repository-url]
- Documentation: http://localhost:5000/health/info
- Health Status: http://localhost:5000/health/detailed

---

**Last Updated:** 2025-01-15  
**API Version:** 1.0.0