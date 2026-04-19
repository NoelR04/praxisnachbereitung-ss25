"""Initial schema für Studierende/Module/Grade."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "20251122_01_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    "student",
    sa.Column("student_id", sa.Integer(), primary_key=True),
    sa.Column("matrikel", sa.Text(), nullable=False, unique=True),
    sa.Column("vorname", sa.Text(), nullable=False),
    sa.Column("nachname", sa.Text(), nullable=False),
    sa.Column("programme", sa.Text(), nullable=False),
    sa.Column("semester", sa.Integer(), nullable=False),
    sa.CheckConstraint("semester between 1 and 12", name="student_semester_check"),
  )

  op.create_table(
    "module",
    sa.Column("module_id", sa.Integer(), primary_key=True),
    sa.Column("name", sa.Text(), nullable=False, unique=True),
  )

  op.create_table(
    "grade",
    sa.Column("grade_id", sa.Integer(), primary_key=True),
    sa.Column("student_id", sa.Integer(), sa.ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False),
    sa.Column("module_id", sa.Integer(), sa.ForeignKey("module.module_id", ondelete="CASCADE"), nullable=False),
    sa.Column("grade_value", sa.Text(), nullable=False),
    sa.Column("graded_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
  )

  conn = op.get_bind()

  # Seed students
  conn.execute(
    text(
      """
      insert into student (matrikel, vorname, nachname, programme, semester) values
        ('12345', 'Anna', 'Koch', 'Informatik', 3),
        ('23456', 'Ben', 'König', 'Wirtschaftsinformatik', 2),
        ('34567', 'Clara', 'Meier', 'Data Science', 4)
      on conflict (matrikel) do nothing;
      """
    )
  )

  # Seed modules
  conn.execute(
    text(
      """
      insert into module (name) values
        ('Datenbanken'),
        ('Programmierung 1'),
        ('Software Engineering'),
        ('Mathematik 1')
      on conflict (name) do nothing;
      """
    )
  )

  # Seed grades using the inserted ids
  conn.execute(
    text(
      """
      insert into grade (student_id, module_id, grade_value)
      select s.student_id, m.module_id, g.grade_value
      from (values
        ('12345', 'Datenbanken',       '1,7'),
        ('12345', 'Programmierung 1',  '2,0'),
        ('23456', 'Datenbanken',       '2,3'),
        ('23456', 'Mathematik 1',      '1,3'),
        ('34567', 'Software Engineering', '1,0')
      ) as g(matrikel, modulname, grade_value)
      join student s on s.matrikel = g.matrikel
      join module m on m.name = g.modulname
      on conflict do nothing;
      """
    )
  )


def downgrade() -> None:
  op.drop_table("grade")
  op.drop_table("module")
  op.drop_table("student")
