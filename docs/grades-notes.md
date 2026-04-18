# Projektanalyse: Grades Starter

## Projektstruktur
Das Projekt ist modular aufgebaut und enthält folgende Hauptkomponenten:
1. **Backend**:
   - **`app/`**: Enthält die Hauptlogik der Anwendung:
     - `main.py`: Definiert die API-Endpunkte und die Hauptlogik.
     - `db.py`: Stellt die Datenbankverbindung bereit.
     - `models.py`: Enthält die Pydantic-Modelle für die Datenvalidierung.
     - `mqtt_integration.py`: Implementiert die MQTT-Integration.
   - **`templates/`**: Beinhaltet die HTML-Templates für die Benutzeroberfläche.
   - **`db/init/`**: SQL-Skripte zur Initialisierung der Datenbank.
   - **`mqtt/`**: Konfigurationsdateien für den MQTT-Broker.
2. **Docker**:
   - `docker-compose.yml` und `Dockerfile` für die Containerisierung.
3. **README.md**: Dokumentation des Projekts.

## Formularverarbeitung
Formulare werden serverseitig verarbeitet:
- **FastAPI** wird verwendet, um Formulardaten zu empfangen. Die Daten werden mit `Form(...)` extrahiert.
- Beispiel: In `main.py` wird ein Formular verarbeitet, um neue Studierende anzulegen:
  ```python
  @app.post("/students", response_class=HTMLResponse)
  def create_student(request: Request, matrikel: str = Form(...), vorname: str = Form(...), ...):
      # Datenbankoperationen
  ```
- **htmx** wird für asynchrone Formularinteraktionen genutzt, z. B. beim Hinzufügen von Noten:
  ```html
  <form hx-post="/grades/htmx" hx-target="#grade-list" hx-swap="innerHTML">
    <input type="text" name="grade_value" required />
    <button type="submit">Note speichern</button>
  </form>
  ```

## Templates
- **Jinja2** wird als Template-Engine verwendet.
- Templates befinden sich im Ordner `templates/` und sind modular aufgebaut:
  - `index.html`: Hauptseite.
  - `grades/`: Enthält Templates für Notenübersicht und -verwaltung.
  - `students/`: Templates für die Verwaltung von Studierenden.
- Templates werden mit `TemplateResponse` gerendert:
  ```python
  return templates.TemplateResponse(
    "students/index.html",
    {"request": request, "students": students},
  )
  ```

## CRUD-Flows
CRUD-Operationen sind für die Entitäten **Studierende**, **Module** und **Noten** implementiert:

### Create
Neue Einträge werden über POST-Requests erstellt:
- Beispiel: Hinzufügen eines neuen Studierenden:
  ```python
  @app.post("/students")
  def create_student(...):
      cur.execute("INSERT INTO student (...) VALUES (...)")
  ```

### Read
Daten werden über SQL-Abfragen aus der Datenbank gelesen und in Templates gerendert:
- Beispiel: Abrufen aller Studierenden:
  ```python
  @app.get("/students")
  def students_page(...):
      cur.execute("SELECT * FROM student")
  ```

### Update
Bearbeitungsformulare senden POST-Requests:
- Beispiel: Aktualisieren eines Studierenden:
  ```python
  @app.post("/students/{student_id}/edit")
  def update_student(...):
      cur.execute("UPDATE student SET ... WHERE student_id = ...")
  ```

### Delete
Einträge werden über POST-Requests gelöscht:
- Beispiel: Löschen eines Studierenden:
  ```python
  @app.post("/students/{student_id}/delete")
  def delete_student(...):
      cur.execute("DELETE FROM student WHERE student_id = ...")
  ```