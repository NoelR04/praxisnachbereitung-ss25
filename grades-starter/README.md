# Grades Starter

Referenzprojekt für **Tag 4** mit einer kleinen Demo-App für die Domäne **Student / Module / Grade**.

Enthalten sind:

- FastAPI
- PostgreSQL
- MQTT (Eclipse Mosquitto)
- Einfacher HTML-Oberfläche (Jinja + htmx)
- Alembic-Migrationen
- CSV-Export `grades.csv`
- Report-/Export-Baustein über `v_grade_report`

Wichtig:

- Dieses Projekt dient als **Blaupause**.
- Für die eigentliche Übung arbeitet ihr auf eurer weiterentwickelten Inventar-App aus Tag 3 weiter.

## Start

Voraussetzungen:

- Docker + Docker Compose
- Alembic läuft im `api`-Container

Dann im Projektordner:

```bash
docker compose up -d --build
```

Schema und Seed-Daten werden anschließend bewusst über Alembic erzeugt:

```bash
docker compose exec api alembic upgrade head
```

Services:

- API: http://localhost:8000
- Postgres: localhost:5432
- MQTT: localhost:1883 (TCP), localhost:9001 (WebSockets)

## Wichtige Endpoints

- `GET /` – Startseite mit Links
- `GET /grades` – UI zum Erfassen und Anzeigen von Noten
- `POST /students` – neuen Studenten anlegen (per Formular)
- `POST /modules` – neues Modul anlegen (per Formular)
- `POST /grades/htmx` – neue Note anlegen (Formular via htmx)
- `GET /grades.csv` – CSV aller Noten inkl. Student- und Modul-Infos
- `GET /grades.xlsx` – XLSX-Datei aller Noten für Power Query / Datei-Import
- `GET /reports/grade-overview` – Report als JSON
- `GET /reports/grade-overview.csv` – flache Export-Tabelle für Excel
- `GET /health` – Health-Check für DB und MQTT
- `GET /docs` – OpenAPI-Dokumentation

## Datenmodell

Tabellen:

- `student (student_id, matrikel, vorname, nachname, programme, semester)`
- `module (module_id, name)`
- `grade (grade_id, student_id, module_id, grade_value, graded_at, attempt)`

Migrationen:

- `20251122_01_initial` – Grundschema + Seed-Daten
- `20251122_02_grade_attempt` – zusätzliche Spalte `attempt`
- `20251122_03_grade_report_view` – View `v_grade_report` für Reports/Exports

## Migrationen mit bestehender DB

Die Postgres-Daten liegen in einem **Named Volume**. Das ist für Tag 4 wichtig:

- `docker compose down`
  stoppt und entfernt Container, **behält aber die DB-Daten**
- `docker compose up -d`
  startet mit denselben Daten weiter
- `docker compose down -v`
  löscht zusätzlich das Volume und setzt die DB vollständig zurück

Typischer Ablauf bei Schema-Änderungen:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

Wenn bereits Daten in der DB liegen, ist das der gewünschte Normalfall:

- Container bei Bedarf neu starten
- Migration ausführen
- Daten behalten

Ein vollständiges Zurücksetzen der DB ist **nicht** nötig und meist auch **nicht** gewünscht.

Falls du einen Schritt zurück demonstrieren willst:

```bash
docker compose exec api alembic downgrade -1
docker compose exec api alembic upgrade head
```

Wichtig:

- `db/init/` wird nur bei einer **frischen, leeren** Postgres-Datenablage ausgewertet.
- Bei bestehendem Volume sind für Schema-Änderungen die **Migrationen** zuständig.

## Reports und Export

Zusätzlich zum bestehenden `grades.csv` gibt es einen klaren Tag-4-Baustein:

- DB-View `v_grade_report`
- JSON-Endpoint `/reports/grade-overview`
- CSV-Endpoint `/reports/grade-overview.csv`
- XLSX-Endpoint `/grades.xlsx`
- Export-Skript `scripts/export_grade_report_to_csv.py`

Der Report liefert eine flache Tabelle mit u. a.:

- `matrikel`
- `student_name`
- `programme`
- `semester`
- `module_name`
- `grade_value`
- `attempt`
- `graded_at`

Damit könnt ihr den Unterschied zwischen
- operativer UI/CRUD-Sicht
- und einer exportfreundlichen Reporting-Sicht

gut als Muster für eure Inventar-App nachvollziehen.

Für eine einfache Power-Query-Demo gibt es zusätzlich `/grades.xlsx` als direkt herunterladbare Datei.
Der Endpoint nutzt `openpyxl` und zeigt bewusst ein kleines, nachvollziehbares Beispiel für den XLSX-Export aus FastAPI.

## MQTT

Die API abonniert beim Start das Topic:

- `grades/new`

Erwartetes Payload-Format (JSON):

```json
{
  "student_id": 1,
  "module_id": 2,
  "grade_value": "1,7"
}
```

Beispiel-Publish (mit `mosquitto_pub`, wenn auf dem Host installiert):

```bash
mosquitto_pub -h localhost -p 1883 -t "grades/new" -m '{"student_id":1,"module_id":2,"grade_value":"1,0"}'
```

Nach erfolgreicher Nachricht sollte auf `/grades` die neue Note erscheinen und im CSV-Export (`/grades.csv`) sichtbar sein.

## Entwicklungsumgebung

Zusätzlich sind enthalten:

- `.devcontainer/` für VS Code Dev Container
- `.vscode/tasks.json` für `compose up`, `compose down`, `logs api`, `logs mqtt`
- `.env` für optionale lokale Overrides
