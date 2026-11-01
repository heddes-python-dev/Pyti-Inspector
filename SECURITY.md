# Sicherheit

## Einsatzgrenzen

Der Inspector ist ein lokales Entwicklungswerkzeug, keine Sandbox und keine
Sicherheitsgrenze. Pyti-Lernskripte laufen weiterhin als normaler Python-Code
mit den Berechtigungen des ausführenden Benutzers.

Der Inspector-Empfänger bindet an `127.0.0.1`, verwendet unverschlüsseltes,
nicht authentifiziertes TCP und begrenzt Events auf 256 KiB. Er ist nicht für
den Betrieb auf einer öffentlichen oder gemeinsam genutzten Netzwerkschnittstelle
ausgelegt. Telemetrie darf keine Geheimnisse oder unnötigen personenbezogenen
Daten enthalten.

## Sicherheitsmeldungen

Melde vermutete Schwachstellen bitte nicht mit ausnutzbaren Details in einem
öffentlichen Issue. Nutze, sofern im GitHub-Projekt aktiviert, die vertrauliche
Meldung unter **Security → Report a vulnerability**. Andernfalls kontaktiere
die Maintainer privat über ihr GitHub-Profil.

Bitte gib eine kurze Beschreibung, betroffene Version, mögliche Auswirkungen
und einen sicheren Weg zur Reproduktion an. Veröffentliche Details erst nach
Abstimmung mit den Maintainer:innen.
