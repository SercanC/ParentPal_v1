"""fix enum issue

Revision ID: 002
Revises: 001
Create Date: 2025-02-26 05:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Work around the enum issue by using text for sync_status temporarily
    op.execute("ALTER TABLE baby ALTER COLUMN sync_status TYPE VARCHAR USING sync_status::VARCHAR")
    
    # Then ALTER it back to the enum but with default value as a string
    op.execute("ALTER TABLE baby ALTER COLUMN sync_status TYPE syncstatus USING sync_status::syncstatus")
    op.execute("ALTER TABLE baby ALTER COLUMN sync_status SET DEFAULT 'pending'")

def downgrade() -> None:
    # No need to do anything in downgrade as we're just fixing the column type
    pass