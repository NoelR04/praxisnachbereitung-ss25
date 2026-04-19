from datetime import datetime

from ..db import get_conn


def _fmt_timestamp(value):
  if value is None:
    return ""
  if isinstance(value, datetime):
    return value.isoformat(sep=" ", timespec="seconds")
  return str(value)


def get_grade_report_rows():
  with get_conn() as conn, conn.cursor() as cur:
    cur.execute(
      """
      select
        matrikel,
        student_name,
        programme,
        semester,
        module_name,
        grade_value,
        attempt,
        graded_at
      from v_grade_report
      order by matrikel, module_name, graded_at
      """
    )
    rows = list(cur.fetchall())

  for row in rows:
    yield {
      "matrikel": row["matrikel"],
      "student_name": row["student_name"],
      "programme": row["programme"],
      "semester": row["semester"],
      "module_name": row["module_name"],
      "grade_value": row["grade_value"],
      "attempt": row["attempt"] or "",
      "graded_at": _fmt_timestamp(row["graded_at"]),
    }


def get_grade_export_fieldnames() -> list[str]:
  return [
    "grade_id",
    "matrikel",
    "vorname",
    "nachname",
    "programme",
    "semester",
    "module_name",
    "grade_value",
    "graded_at",
  ]


def get_grade_export_rows():
  with get_conn() as conn, conn.cursor() as cur:
    cur.execute(
      """
      select g.grade_id,
             s.matrikel,
             s.vorname,
             s.nachname,
             s.programme,
             s.semester,
             m.name as module_name,
             g.grade_value,
             g.graded_at
      from grade g
      join student s on s.student_id = g.student_id
      join module m on m.module_id = g.module_id
      order by s.matrikel, m.name, g.graded_at
      """
    )
    return list(cur.fetchall())


def export_cell_value(field_name, value):
  if value is None:
    return None
  if field_name == "grade_value":
    if isinstance(value, (int, float)):
      return float(value)
    return float(str(value).replace(",", "."))
  return value
