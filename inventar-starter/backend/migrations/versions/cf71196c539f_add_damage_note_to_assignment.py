"""add_damage_note_to_assignment

Revision ID: cf71196c539f
Revises: 
Create Date: 2026-04-19 09:37:03.979080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf71196c539f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE assignment 
        ADD COLUMN damage_note TEXT
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE assignment 
        DROP COLUMN damage_note
    """)
