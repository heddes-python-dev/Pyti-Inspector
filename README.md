# Pyti Inspector

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Lizenz](https://img.shields.io/badge/Lizenz-MIT-green)

Ein eigenständiges Desktop-Dashboard für Pyti-Telemetrie, Ablaufereignisse und
Zustandsdaten. Dieses Projekt liegt außerhalb des
[Pyti-Lernumgebungs-Repositories](https://github.com/heddes-python-dev/pyti_lernumgebung)
und ändert keine Pyti-Dateien. Die optionale Laufzeit-Anbindung erfolgt über
einen externen Launcher; alternativ lässt sich der Inspector mit einem
Demo-Sender unabhängig ausprobieren.

**Version:** siehe [VERSION](VERSION) · **Lizenz:** [MIT](LICENSE)

## Dokumentation

- [Benutzerhandbuch](USER_GUIDE.md): Installation, Start, Pyti-Anbindung und
  Fehlerbehebung
- [Protokollversion 1](#schnittstelle-version-1): Event-Schema für eigene Sender
- [Roadmap](ROADMAP.md): geplante Entwicklung und bekannte Grenzen
- [Mitwirken](CONTRIBUTING.md): lokale Entwicklung, Tests und Pull Requests
- [Sicherheitsrichtlinie](SECURITY.md): Umgang mit Telemetrie und Meldungen

## Good First Issues

Du möchtest mithelfen? Diese kleinen, abgegrenzten Aufgaben sind ein guter
Einstieg. Auf GitHub findest du weitere Tickets mit dem Label
[good first issue](https://github.com/heddes-python-dev/Pyti-Inspector/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

- [Event-Typen in der Timeline filtern](https://github.com/heddes-python-dev/Pyti-Inspector/issues/1)
- [Timeline leeren, ohne die Verbindung zu trennen](https://github.com/heddes-python-dev/Pyti-Inspector/issues/2)
- [Fehlerhafte und zu große Telemetrie-Nachrichten testen](https://github.com/heddes-python-dev/Pyti-Inspector/issues/3)
- [Screenshot und Demo-Anleitung ergänzen](https://github.com/heddes-python-dev/Pyti-Inspector/issues/4)

Lies vor deinem Beitrag den [Mitwirkungsleitfaden](CONTRIBUTING.md). Kommentiere
das gewünschte Issue vor Beginn, damit andere sehen, dass du daran arbeitest.

## Starten

Benötigt Python 3.10+ und PySide6:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

In einem zweiten Terminal:

```bash
python demo_sender.py
```

Unter Windows PowerShell kann die virtuelle Umgebung mit
`.venv\Scripts\Activate.ps1` aktiviert werden.

## Pyti ohne Änderungen am Pyti-Repository anbinden

Der externe Launcher startet Inspector und Pyti gemeinsam. Er instrumentiert den
geladenen Pyti-Interpreter nur im Arbeitsspeicher; keine Pyti-Datei wird
bearbeitet:

```bash
python launch_pyti.py /absoluter/pfad/zu/pyti_lernprogramm
```

Wähle in Pyti ein Level und starte ein Skript. Der Inspector zeigt dessen
Quelltextzeilen, Aktionen und Sensorergebnisse, JSON-taugliche lokale
Skriptvariablen, Roboterposition, Blickrichtung, Beeper, Wände sowie Fehler an.
Ohne den Launcher gestartetes Pyti bleibt unverändert und sendet nichts.

Beide Anwendungen werden mit demselben Python-Interpreter gestartet. Dieser
muss PySide6 und die in Pyti benötigten Pakete installiert haben.
Schritt-für-Schritt-Anweisungen stehen im [Benutzerhandbuch](USER_GUIDE.md).

## Funktionen

- Echtzeit-Eventliste mit Programmzeile, Aktion/Sensor und Rückgabewert
- Variablen-Watcher für die zuletzt gemeldeten JSON-serialisierbaren Werte
- Event-, Aktions-, X- und Y-Bewegungsschrittzähler, Laufzeit und
  Fehler-/Traceback-Anzeige
- Bis zu 1000 letzte Events im Inspector-Fenster
- JSON-Lines-Protokoll über TCP, ausschließlich an `127.0.0.1`
- Keine Änderung oder Abhängigkeit von der Pyti-Lernumgebung

Die Pyti-Laufzeit-Anbindung ist ein externer Adapter. Sie liest keine
Call-Stack-Objekte aus und stellt keinen interaktiven Debugger bereit. Bei
Fehlern werden Pyti-Fehlerdetails, die zuletzt bekannte Skriptzeile und der
Python-Traceback des fehlgeschlagenen Befehls übertragen. Für andere Programme
muss der Sender passende `line`, `state`, `variables` und `error` Events
explizit liefern.

## Schnittstelle, Version 1

Der Inspector lauscht auf `127.0.0.1:8765`. Jedes Event ist ein UTF-8-JSON-
Objekt, abgeschlossen durch einen Zeilenumbruch. Jede Nachricht muss `version`
und `type` enthalten. Unterstützte Typen:

- `session_start`: Skriptlauf beginnt
- `line`: ausgeführte Quelltextzeile; optional `line`, `variables`
- `action`: Befehl wie `moveForward`; erforderlich `name`, optional `line`,
  `state`, `variables`
- `sensor`: Sensorabfrage; erforderlich `name`, optional `result`, `line`
- `state`: Zustands-/Variablen-Snapshot
- `error`: erforderlich `message`, optional `line`, `traceback`
- `session_end`: Skriptlauf endet

Beispiel:

```json
{"version":1,"type":"sensor","name":"frontClear","result":true,"line":12,"variables":{"x":2}}
```

Sender können den mitgelieferten `TelemetryClient` verwenden. Das Protokoll
transportiert JSON-Daten und darf keine Passwörter, Tokens oder sonstige
Geheimnisse enthalten. Der Listener ist an Loopback gebunden und nimmt
Nachrichten bis 256 KiB pro Event an.

## Tests

```bash
python -m unittest discover -s tests -v
```
