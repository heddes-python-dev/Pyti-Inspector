# Mitwirken

Fehlerberichte, Verbesserungsvorschläge, Dokumentation und Codebeiträge sind
willkommen. Beschreibe bei Fehlern Schritte zur Reproduktion, Python-Version
und Betriebssystem. Teile keine Zugangsdaten oder persönlichen Daten.

## Lokal entwickeln

```bash
git clone https://github.com/heddes-python-dev/Pyti-Inspector.git
cd Pyti-Inspector
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell: `.venv\Scripts\Activate.ps1`.

Erstelle für Änderungen einen Branch:

```bash
git switch -c feature/kurze-beschreibung
```

## Prüfungen

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
git diff --check
```

Für Qt-Tests ohne Bildschirm:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

Neue Funktionen sollten passende Tests enthalten. Änderungen am JSON-Lines-
Protokoll müssen die Protokollversion und Kompatibilität berücksichtigen.
Änderungen an Pyti müssen den externen, optionalen Charakter des Adapters
erhalten: Beiträge zu diesem Repository dürfen nicht voraussetzen, dass
Pyti-Dateien gepatcht oder Telemetrie standardmäßig aktiviert werden.

## Pull Request

1. Führe die Prüfungen aus und beschreibe relevante Ergebnisse.
2. Committe mit einer kurzen, aussagekräftigen Nachricht.
3. Push deinen Branch zu deinem Fork und öffne einen Pull Request nach
   `heddes-python-dev/Pyti-Inspector:main`.
4. Füge bei Änderungen der Oberfläche nach Möglichkeit einen Screenshot bei.
