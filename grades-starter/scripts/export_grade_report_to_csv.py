import csv
import os
from datetime import datetime

import psycopg


DSN = os.getenv("DB_DSN", "postgresql://appuser:apppass@localhost:5432/appdb")
OUT_DIR = os.getenv("EXPORT_DIR", "exports")


def main():
  os.makedirs(OUT_DIR, exist_ok=True)
  ts = datetime.now().strftime("%Y-%m-%d")
  out_path = os.path.join(OUT_DIR, f"grade_overview_{ts}.csv")

  with psycopg.connect(DSN) as conn, conn.cursor() as cur:
    cur.execute("select * from v_grade_report order by matrikel, module_name, graded_at")
    cols = [desc[0] for desc in cur.description]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
      writer = csv.writer(f, delimiter=";")
      writer.writerow(cols)
      for row in cur:
        writer.writerow(row)

  print(f"Export OK -> {out_path}")


if __name__ == "__main__":
  main()
