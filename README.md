# ETL mit Excel & Git – Praxisnachbereitung SS25

## Ziel der Übung

Ziel dieser Übung war es, unbereinigte CSV-Daten in Excel zu importieren, zu bereinigen, zusammenzuführen und anschließend visuell auszuwerten. 

## Vorgehen

### 1. Datenimport

Die drei CSV-Dateien (**Geraete**, **Ausleihen**, **Mitarbeiter**) wurden über
**Daten → Aus Text/CSV** in Excel importiert.

Jede Datei wurde auf ein eigenes Tabellenblatt geladen.

---

### 2. Datenbereinigung

Folgende Schritte wurden durchgeführt:

* Entfernen von komplett leeren Zeilen
* Vereinheitlichung der Spaltenüberschriften
* Überprüfung der Datentypen:

  * IDs als Zahlen
  * Datumswerte als Datum
  * Preise als Zahlen

---

### 3. Datenzusammenführung

#### Geräte + Ausleihen

Die Tabellen wurden über die **Gerätenummer** verknüpft (SVERWEIS).

#### Mitarbeiter ergänzen

Die Mitarbeiterdaten wurden über die **Mitarbeiter-ID** ergänzt.

Ergebnis:

* Eine vollständige Gesamttabelle mit allen relevanten Informationen

---

## 4. Analyse (Teil D)

### Gesamtwert nicht im Einsatz befindlicher Geräte

Es wurde nach Geräten mit Rückgabedatum gefiltert.

Vorgehen:

* Filter auf Spalte **„Rückgabe am“**
* Auswahl: alle außer leere Werte
* Summierung der Spalte **Netto-Kaufpreis**

**Ergebnis:**
→ Gesamtwert: **36.846,17 €**

---

### Analyse: Laptop-Ausleihen

Es wurde nach Gerätetyp **„Laptop“** gefiltert.

Auffälligkeiten:

* Gerätenummer **G0004** weist eine unplausible Ausleihe auf, da er 2 mal im gleichen Zeitraum ausgeliehen wurde.
* Gerät **G0031** wurde mehrfach ausgeliehen, ohne zwischendurch zurückgegeben zu werden.

---

### Pivot-Auswertung

Es wurde eine Pivot-Tabelle erstellt:

* Zeilen: Gerätetyp
* Werte: Anzahl der Ausleihen

Zusätzlich:

* Erweiterung um Standort
* Visualisierung mittels Diagramm

---

## Erkenntnisse

* Formatfehler (z. B. Text vs. Zahl) führen zu großen Problemen (#NV)
* Pivot-Tabellen sind leicht zu erstellen und sind übersichtlich.
* Plausibilitätsprüfungen sind notwendig bevor mit Daten gearbeitet werden können

---

## Git-Dokumentation

* Initialer Commit: Startdateien
* Weitere Commits: Datenbereinigung, Zusammenführung, Analyse
* README dokumentiert den gesamten Workflow
