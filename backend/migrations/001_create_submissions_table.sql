-- SubmitEZ Database Migration: Create Submissions Table
-- Version: 001
-- Description: Initial schema for submissions with JSONB columns for flexible data storage
-- Author: SubmitEZ Team
-- Date: 2025-01-15

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Workflow Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    
    -- Core Data (JSONB for flexibility)
    applicant JSONB,
    locations JSONB DEFAULT '[]'::jsonb,
    coverage JSONB,
    loss_history JSONB DEFAULT '[]'::jsonb,
    
    -- File References
    uploaded_files JSONB DEFAULT '[]'::jsonb,
    generated_files JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    extracted_at TIMESTAMPTZ,
    validated_at TIMESTAMPTZ,
    generated_at TIMESTAMPTZ,
    
    -- Validation Results
    validation_errors JSONB DEFAULT '[]'::jsonb,
    validation_warnings JSONB DEFAULT '[]'::jsonb,
    is_valid BOOLEAN DEFAULT FALSE,
    
    -- Extraction Metadata
    extraction_metadata JSONB DEFAULT '{}'::jsonb,
    extraction_confidence DECIMAL(3,2),
    
    -- Additional Information
    broker_name VARCHAR(200),
    broker_email VARCHAR(255),
    carrier_name VARCHAR(200),
    effective_date_requested VARCHAR(50),
    
    -- Notes
    notes TEXT,
    internal_notes TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (
        status IN (
            'draft', 
            'uploaded', 
            'extracting', 
            'extracted', 
            'validating', 
            'validated', 
            'generating', 
            'completed', 
            'error'
        )
    ),
    CONSTRAINT valid_confidence CHECK (
        extraction_confidence IS NULL OR 
        (extraction_confidence >= 0 AND extraction_confidence <= 1)
    )
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_updated_at ON submissions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_broker_email ON submissions(broker_email);
CREATE INDEX IF NOT EXISTS idx_submissions_is_valid ON submissions(is_valid);

-- Create GIN indexes for JSONB columns (enables fast searches within JSON)
CREATE INDEX IF NOT EXISTS idx_submissions_applicant_gin ON submissions USING GIN (applicant);
CREATE INDEX IF NOT EXISTS idx_submissions_locations_gin ON submissions USING GIN (locations);
CREATE INDEX IF NOT EXISTS idx_submissions_coverage_gin ON submissions USING GIN (coverage);
CREATE INDEX IF NOT EXISTS idx_submissions_metadata_gin ON submissions USING GIN (metadata);

-- Create specific JSONB path indexes for common queries
CREATE INDEX IF NOT EXISTS idx_submissions_applicant_business_name 
    ON submissions ((applicant->>'business_name'));
CREATE INDEX IF NOT EXISTS idx_submissions_applicant_fein 
    ON submissions ((applicant->>'fein'));

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function before any update
CREATE TRIGGER set_submissions_updated_at
    BEFORE UPDATE ON submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function for submission statistics
CREATE OR REPLACE FUNCTION get_submission_stats()
RETURNS TABLE (
    total_count BIGINT,
    status VARCHAR(50),
    status_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM submissions)::BIGINT as total_count,
        s.status,
        COUNT(*)::BIGINT as status_count
    FROM submissions s
    GROUP BY s.status
    ORDER BY status_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE submissions IS 'Main table for insurance submission data';
COMMENT ON COLUMN submissions.id IS 'Unique submission identifier (UUID)';
COMMENT ON COLUMN submissions.status IS 'Current workflow status of submission';
COMMENT ON COLUMN submissions.applicant IS 'Applicant/insured information as JSONB';
COMMENT ON COLUMN submissions.locations IS 'Array of property locations as JSONB';
COMMENT ON COLUMN submissions.coverage IS 'Coverage details as JSONB';
COMMENT ON COLUMN submissions.loss_history IS 'Array of loss/claim history as JSONB';
COMMENT ON COLUMN submissions.uploaded_files IS 'Array of uploaded file references';
COMMENT ON COLUMN submissions.generated_files IS 'Array of generated output file references';
COMMENT ON COLUMN submissions.extraction_confidence IS 'Overall extraction confidence score (0-1)';
COMMENT ON COLUMN submissions.is_valid IS 'Whether submission passed validation';

-- Grant permissions (adjust based on your security requirements)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON submissions TO submitez_app_user;
-- GRANT USAGE ON SEQUENCE submissions_id_seq TO submitez_app_user;

-- Insert sample data for testing (optional - remove in production)
-- INSERT INTO submissions (status, notes) VALUES ('draft', 'Sample submission for testing');

-- Verify table creation
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename = 'submissions';

-- Verify indexes
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'submissions'
ORDER BY indexname;

-- Display table structure
-- \d submissions;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration 001: Submissions table created successfully';
    RAISE NOTICE 'Indexes created for optimal query performance';
    RAISE NOTICE 'Triggers configured for automatic timestamp updates';
END $$;