"""Add report view for grade exports."""

from alembic import op


revision = "20251122_03_grade_report_view"
down_revision = "20251122_02_grade_attempt"
branch_labels = None
depends_on = None


def upgrade():
  op.execute(
    """
    create or replace view v_grade_report as
    select
      s.matrikel,
      s.vorname || ' ' || s.nachname as student_name,
      s.programme,
      s.semester,
      m.name as module_name,
      g.grade_value,
      coalesce(g.attempt, 1) as attempt,
      g.graded_at
    from grade g
    join student s on s.student_id = g.student_id
    join module m on m.module_id = g.module_id
    order by s.matrikel, m.name, g.graded_at;
    """
  )


def downgrade():
  op.execute("drop view if exists v_grade_report")
