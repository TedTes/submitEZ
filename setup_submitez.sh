#!/bin/bash

# SubmitEZ MVP - Project Structure Generator
# Creates complete folder structure without content
# Run: chmod +x setup_submitez.sh && ./setup_submitez.sh

echo "╔═══════════════════════════════════════╗"
echo "║      SubmitEZ MVP Setup Script        ║"
echo "║  Insurance Submission Automation      ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create root directory
echo -e "${BLUE}📁 Creating root directory...${NC}"


# ========================================
# BACKEND STRUCTURE
# ========================================
echo -e "${BLUE}📦 Creating backend structure...${NC}"

# Main app directories
mkdir -p backend/app/api/{routes,middleware}
mkdir -p backend/app/core/{services,processors}
mkdir -p backend/app/domain/{models,schemas}
mkdir -p backend/app/infrastructure/database/repositories
mkdir -p backend/app/infrastructure/{storage,ai,pdf}
mkdir -p backend/app/utils

# Test directories
mkdir -p backend/tests/{unit,integration,fixtures}

# Migrations
mkdir -p backend/migrations

# Create all __init__.py files for Python packages
echo -e "${YELLOW}  → Creating Python package files...${NC}"
find backend/app -type d -exec touch {}/__init__.py \;
touch backend/tests/__init__.py

# Create empty Python files
echo -e "${YELLOW}  → Creating empty Python modules...${NC}"

# API Layer
touch backend/app/api/routes/{__init__.py,submission_routes.py,health_routes.py}
touch backend/app/api/middleware/{__init__.py,error_handler.py,request_validator.py}

# Core Layer
touch backend/app/core/services/{__init__.py,submission_service.py,extraction_service.py,validation_service.py,generation_service.py}
touch backend/app/core/processors/{__init__.py,base_processor.py,pdf_processor.py,excel_processor.py,acord_processor.py,processor_factory.py}

# Domain Layer
touch backend/app/domain/models/{__init__.py,submission.py,applicant.py,property_location.py,coverage.py,loss_history.py}
touch backend/app/domain/schemas/{__init__.py,submission_schema.py,extraction_schema.py,validation_schema.py}

# Infrastructure Layer
touch backend/app/infrastructure/database/{__init__.py,supabase_client.py}
touch backend/app/infrastructure/database/repositories/{__init__.py,base_repository.py,submission_repository.py}
touch backend/app/infrastructure/storage/{__init__.py,base_storage.py,supabase_storage.py}
touch backend/app/infrastructure/ai/{__init__.py,base_llm.py,openai_client.py,prompt_templates.py}
touch backend/app/infrastructure/pdf/{__init__.py,base_pdf_generator.py,acord_generator.py,carrier_generator.py}

# Utils
touch backend/app/utils/{__init__.py,file_utils.py,validation_utils.py,logger.py}

# Root app files
touch backend/app/{__init__.py,config.py}

# Root backend files
touch backend/{run.py,wsgi.py,requirements.txt,requirements-dev.txt,.env.example,.gitignore}

# Test files
touch backend/tests/unit/.gitkeep
touch backend/tests/integration/.gitkeep
touch backend/tests/fixtures/.gitkeep

echo -e "${GREEN}✓ Backend structure created${NC}"

# ========================================
# FRONTEND STRUCTURE
# ========================================
echo -e "${BLUE}🎨 Creating frontend structure...${NC}"

# App router structure
mkdir -p frontend/src/app/{api,'(routes)'/{upload,review,download}}
mkdir -p frontend/public/assets

# Components
mkdir -p frontend/src/components/{ui,layout,upload,review,download}

# Lib
mkdir -p frontend/src/lib/{api,utils}

# Hooks
mkdir -p frontend/src/hooks

# Types
mkdir -p frontend/src/types

# Styles
mkdir -p frontend/src/styles

echo -e "${YELLOW}  → Creating TypeScript/React files...${NC}"

# App files
touch frontend/src/app/{layout.tsx,page.tsx,globals.css}
touch frontend/src/app/'(routes)'/upload/page.tsx
touch frontend/src/app/'(routes)'/review/page.tsx
touch frontend/src/app/'(routes)'/download/page.tsx

# Layout components
touch frontend/src/components/layout/{Header.tsx,Footer.tsx}

# Upload components
touch frontend/src/components/upload/{FileUploader.tsx,FileList.tsx}

# Review components
touch frontend/src/components/review/{DataReviewTable.tsx,ValidationErrors.tsx,EditableField.tsx}

# Download components
touch frontend/src/components/download/{DocumentPreview.tsx,DownloadButton.tsx}

# UI components (shadcn placeholders)
touch frontend/src/components/ui/{button.tsx,card.tsx,input.tsx,table.tsx,alert.tsx}

# Lib files
touch frontend/src/lib/api/{client.ts,submission-api.ts,types.ts}
touch frontend/src/lib/utils/{format.ts,validation.ts}
touch frontend/src/lib/constants.ts
touch frontend/src/lib/utils.ts

# Hooks
touch frontend/src/hooks/{useSubmission.ts,useFileUpload.ts,useValidation.ts}

# Types
touch frontend/src/types/{submission.ts,extraction.ts,api.ts}

# Styles
touch frontend/src/styles/globals.css

# Root frontend files
touch frontend/{next.config.js,package.json,tsconfig.json,tailwind.config.ts,postcss.config.js,.env.local.example,.gitignore,.eslintrc.json}

# Public assets
touch frontend/public/assets/.gitkeep

echo -e "${GREEN}✓ Frontend structure created${NC}"

# ========================================
# DOCUMENTATION
# ========================================
echo -e "${BLUE}📚 Creating documentation...${NC}"

mkdir -p docs

touch docs/{API.md,ARCHITECTURE.md,SETUP.md,DEPLOYMENT.md}
touch README.md
touch .gitignore

echo -e "${GREEN}✓ Documentation structure created${NC}"

# ========================================
# ROOT CONFIGURATION
# ========================================
echo -e "${BLUE}⚙️  Creating root configuration files...${NC}"

touch {.gitignore,.gitattributes,docker-compose.yml,Makefile}

# Create .gitkeep files for empty directories that need to be tracked
find . -type d -empty -exec touch {}/.gitkeep \;

echo -e "${GREEN}✓ Root configuration created${NC}"

# ========================================
# SUMMARY
# ========================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ SubmitEZ Structure Created!       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📁 Project Structure:${NC}"
echo "   submitez-mvp/"
echo "   ├── backend/          (Python/Flask API)"
echo "   │   ├── app/"
echo "   │   │   ├── api/           (Routes & Middleware)"
echo "   │   │   ├── core/          (Services & Processors)"
echo "   │   │   ├── domain/        (Models & Schemas)"
echo "   │   │   ├── infrastructure/(Database, Storage, AI, PDF)"
echo "   │   │   └── utils/         (Utilities)"
echo "   │   ├── tests/"
echo "   │   └── migrations/"
echo "   ├── frontend/         (Next.js TypeScript)"
echo "   │   └── src/"
echo "   │       ├── app/           (App Router)"
echo "   │       ├── components/    (React Components)"
echo "   │       ├── lib/           (API & Utils)"
echo "   │       ├── hooks/         (Custom Hooks)"
echo "   │       └── types/         (TypeScript Types)"
echo "   └── docs/             (Documentation)"
echo ""
echo -e "${YELLOW}📊 Statistics:${NC}"
echo "   Backend files:  $(find backend -type f | wc -l | tr -d ' ')"
echo "   Frontend files: $(find frontend -type f | wc -l | tr -d ' ')"
echo "   Total files:    $(find . -type f | wc -l | tr -d ' ')"
echo ""
echo -e "${BLUE}🎯 Next Steps:${NC}"



echo ""
echo -e "${GREEN}✨ Structure ready for incremental development!${NC}"