# Pyti Inspector – Benutzerhandbuch

Der Pyti Inspector ist ein separates Desktop-Programm. Er empfängt
Telemetrieereignisse auf dem lokalen Rechner und zeigt Ablauf, Sensoren,
Variablen, Roboterzustand und Fehler an. Er ändert keine Pyti-Dateien.

## Voraussetzungen

- Python 3.10 oder neuer
- PySide6 6.11.0
- Für die Pyti-Anbindung: eine lokale Pyti-Lernumgebung und deren
  Python-Abhängigkeiten

## Installation

Wechsle in das Verzeichnis des Inspector-Projekts und richte eine virtuelle
Umgebung ein:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Installiere anschließend PySide6:

```bash
python -m pip install -r requirements.txt
```

## Inspector unabhängig ausprobieren

Starte den Inspector:

```bash
python main.py
```

In einem zweiten Terminal, im selben Projektverzeichnis und mit derselben
aktivierten Umgebung:

```bash
python demo_sender.py
```

Das Dashboard sollte Beispielereignisse, Variablen, Roboterposition und einen
Beispielfehler anzeigen.

## Pyti verbinden

1. Stelle sicher, dass Pyti und der Inspector im selben Python-Interpreter
   benötigte Abhängigkeiten installiert haben. Pyti benötigt PySide6.
2. Starte beide Programme über den Launcher:

   ```bash
   python launch_pyti.py "/absoluter/pfad/zu/pyti_lernprogramm"
   ```

3. Wähle in Pyti ein Level und starte ein Skript.
4. Beobachte Zeilen, Pyti-Befehle, Sensorergebnisse, Variablen und Zustand im
   Inspector-Fenster.

Der Launcher startet den Inspector und Pyti als getrennte Prozesse. Der
Adapter importiert den Pyti-Interpreter und instrumentiert ihn zur Laufzeit im
Arbeitsspeicher. Er speichert, patcht oder überschreibt keine Pyti-Dateien.
Ohne den Launcher sendet Pyti keine Inspector-Telemetrie. Ist der Inspector
nicht erreichbar, läuft Pyti ohne Telemetrie weiter.

## Dashboard

- **Events:** Zeit, Eventtyp, Aktion/Sensor, Ergebnis und Python-Zeile.
- **Variablen:** zuletzt vom Sender gemeldete JSON-Werte und Zustandsfelder.
- **Metriken:** Eventzahl, Aktionen/Sensoren, X- und Y-Bewegungsschritte,
  Laufzeit und Frequenz. Sprünge zählen entsprechend der zurückgelegten
  Koordinatendifferenz; jede Sitzung beginnt bei null.
- **Fehler:** Fehlermeldung und vom Sender gelieferte Traceback-Informationen.

Das Dashboard hält höchstens 1000 Events. Der Inspector pausiert die
Programmausführung nicht und zeigt keinen vollständigen interaktiven
Python-Call-Stack. Komplexe Objekte werden begrenzt dargestellt; große
Sammlungen sind gekürzt.

## Protokoll

Der Empfänger lauscht auf `127.0.0.1:8765`. Jedes Event ist ein UTF-8-JSON-
Objekt auf einer Zeile, höchstens 256 KiB groß. Erforderliche Felder:

```json
{"version":1,"type":"sensor","name":"frontClear","result":true,"line":12,"variables":{"x":2}}
```

`version` muss `1` sein. Unterstützte Typen und Felder:

| Typ | Pflichtfelder | Optionale Nutzdaten |
|---|---|---|
| `session_start` | – | `message`, `session_id` |
| `line` | – | `line`, `variables` |
| `action` | `name` | `line`, `result`, `state`, `variables` |
| `sensor` | `name` | `line`, `result`, `state`, `variables` |
| `state` | – | `state`, `variables` |
| `error` | `message` | `line`, `traceback` |
| `session_end` | – | `message`, `state` |

Der mitgelieferte `TelemetryClient` nimmt eine Verbindung zu `127.0.0.1:8765`
auf und validiert Events vor dem Senden.

## Fehlerbehebung

- **Inspector startet nicht:** Prüfe Installation und Qt-Unterstützung mit
  `python -m pip show PySide6`.
- **Port belegt:** Eine andere Anwendung verwendet `127.0.0.1:8765`; beende
  sie vor dem Start des Inspectors.
- **Keine Events:** Starte Pyti mit `launch_pyti.py`, verwende für beide
  Programme denselben Python-Interpreter und starte anschließend ein Skript.
- **Telemetrieverbindung fehlt:** Prüfe, ob der Inspector läuft und die lokale
  Verbindung auf Loopback nicht durch lokale Sicherheitssoftware blockiert ist.

## Sicherheit und Datenschutz

Die Verbindung ist unverschlüsselt, nicht authentifiziert und nur an Loopback
gebunden. Sie ist für den lokalen Rechner vorgesehen, nicht für ein Netzwerk.
Sende keine Passwörter, Zugriffstoken oder persönlichen Daten. Pyti führt
Lernskripte als normalen Python-Code aus und ist keine Sandbox. Führe nur
Skripte aus, denen du vertraust.
