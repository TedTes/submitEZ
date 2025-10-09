"""create submissions table

Revision ID: abc123
Revises: 
Create Date: 2025-01-15 12:34:56

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration - read from SQL file"""
    # Read and execute the SQL file
    with open('migrations/001_create_submissions_table.sql', 'r') as f:
        sql = f.read()
        
    # Execute the SQL
    op.execute(sql)


def downgrade() -> None:
    """Rollback migration"""
    op.drop_table('submissions')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE')
    op.execute('DROP FUNCTION IF EXISTS get_submission_stats() CASCADE')