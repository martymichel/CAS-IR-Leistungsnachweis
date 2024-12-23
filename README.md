
# README: CAS Search Engine

## Inhaltsverzeichnis

1. **Daten indexieren**
2. **Indexdaten testen (optional)**
3. **Suchmaschine im Browser starten**

---

## 1. Daten indexieren

Das Skript `directory_indexer.py` wird verwendet, um Dateien aus verschiedenen Verzeichnissen zu indexieren und in einem Whoosh-kompatiblen Index zu speichern.

### Schritte:

1. **Skript starten**:
   ```bash
   python directory_indexer.py
   ```
2. **Ordner auswählen**:
   - Es erscheint ein Dialogfenster, in dem mehrere Verzeichnisse ausgewählt werden können.
   - Nach der Auswahl eines Verzeichnisses können Sie weitere hinzufügen oder fortfahren.
3. **Speicherort für den Index festlegen**:
   - Wählen Sie ein Zielverzeichnis, in dem der Index gespeichert wird.

### Unterstützte Dateitypen:

- `.pdf`
- `.txt`
- `.csv`
- `.py`
- `.ipynb`
- `.html`
- `.r`
- `.qmd`
- `.pptx`

### Fehlerbehandlung:

- Nicht unterstützte oder fehlerhafte Dateien werden protokolliert.
- Eine Protokolldatei `error_log.txt` wird im Indexspeicherort erstellt.

---

## 2. Indexdaten testen (optional)

Das Skript `test_whoosh.py` überprüft den Inhalt des erstellten Index.

### Schritte:

1. **Skript starten**:
   ```bash
   python test_whoosh.py
   ```
2. **Pfad zum Index eingeben**:
   - Geben Sie den Pfad zum erstellten Index ein.
3. **Ausgabe analysieren**:
   - Zeigt eine Übersicht der gespeicherten Felder und eine Vorschau der ersten fünf Dokumente im Index.

---

## 3. Suchmaschine im Browser starten

Das Skript `whoosh_search.py` startet eine Flask-Webanwendung, die die Suche im Index ermöglicht.

### Schritte:

1. **Skript starten**:
   ```bash
   python whoosh_search.py
   ```
2. **Browser öffnen**:
   - Navigieren Sie zu `http://127.0.0.1:5000`.
3. **Suchanfragen stellen**:
   - Geben Sie den Suchbegriff in das Suchfeld ein.
   - Ergebnisse werden im Browser angezeigt.

### Hinweise:

- Stellen Sie sicher, dass der Index erstellt wurde und der Pfad im Skript korrekt ist:
  ```python
  index_dir = r"P:\PY\CAS IR Leistungsnachweis\whoosh_index"
  ```
- Fehlerhafte oder unvollständige Suchanfragen werden behandelt, und entsprechende Fehlermeldungen werden angezeigt.

---

## Kontakt

Bei Problemen oder Fragen wenden Sie sich an den Entwickler. Viel Erfolg bei der Nutzung der CAS Search Engine!
