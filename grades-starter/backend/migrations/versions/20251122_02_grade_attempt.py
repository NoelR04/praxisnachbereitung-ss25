from alembic import op
import sqlalchemy as sa

revision = "20251122_02_grade_attempt"
down_revision = "20251122_01_initial"
branch_labels = None
depends_on = None

def upgrade():
  op.add_column(
    "grade",
    sa.Column("attempt", sa.Integer(), nullable=True),
  )

def downgrade():
  op.drop_column("grade", "attempt")
