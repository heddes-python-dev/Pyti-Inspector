# Roadmap

Diese Roadmap beschreibt mögliche nächste Schritte. Sie ist keine verbindliche
Terminplanung; Rückmeldungen und Beiträge sind willkommen.

## 0.1.x – Stabilisierung

- [x] Eigenständiges Dashboard und lokaler JSON-Lines-Empfänger
- [x] Externer Pyti-Launcher ohne Änderungen am Pyti-Repository
- [x] Demo-Sender, Tests, Benutzer- und Sicherheitsdokumentation
- [ ] Installation und Bedienung auf Windows und macOS erproben
- [ ] Screenshots und kurze Demo für neue Nutzer ergänzen

## 0.2 – Bedienbarkeit

- [ ] Events nach Typ filtern und die Ansicht löschen/exportieren
- [ ] Konfigurierbarer lokaler Port mit eindeutiger Fehleranzeige
- [ ] Ereignisdetails und Variablenwerte komfortabler anzeigen
- [ ] Laufzeitmetriken in einer Zeitachse darstellen

## 0.3 – Protokoll und Integrationen

- [ ] Protokollschema mit Beispielen und Kompatibilitätsregeln stabilisieren
- [ ] Gezielte Tests für ungültige, große und getrennte Client-Nachrichten
- [ ] Adapter-Schnittstelle für weitere lokale Lernprogramme dokumentieren
- [ ] Optionalen Export von Telemetriesitzungen entwerfen

## Grenzen und Voraussetzungen

- Das Tool ist ein Entwicklungs- und Lernwerkzeug, keine Sicherheits-Sandbox.
- Der Empfänger ist für lokalen Gebrauch an `127.0.0.1` gebunden und nicht
  authentifiziert.
- Variablen, Zustände und Fehler werden nur angezeigt, wenn der Sender sie
  überträgt. Der Inspector liefert keinen interaktiven Call-Stack.
- Pyti-Skripte bleiben normaler Python-Code; nur vertrauenswürdige Skripte
  ausführen.
