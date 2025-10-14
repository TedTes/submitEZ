"""add_client_name_to_submissions

Revision ID: c3ed138351a6
Revises: abc123
Create Date: 2025-10-14 11:56:41.258468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3ed138351a6'
down_revision: Union[str, None] = 'abc123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add client_name column to submissions table"""
    # Add client_name column (nullable initially to handle existing rows)
    op.add_column(
        'submissions',
        sa.Column('client_name', sa.String(length=200), nullable=True)
    )
    
    # Optional: Create index for faster searches by client name
    op.create_index(
        'ix_submissions_client_name',
        'submissions',
        ['client_name'],
        unique=False
    )


def downgrade() -> None:
    """Remove client_name column from submissions table"""
    # Drop index first
    op.drop_index('ix_submissions_client_name', table_name='submissions')
    
    # Drop column
    op.drop_column('submissions', 'client_name')