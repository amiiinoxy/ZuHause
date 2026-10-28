# XO · Spielraum

Website: https://amiiinoxy.github.io/ZuHause/XO/

Die statische Spielseite liegt auf dem Veröffentlichungsbranch `wohnortvergleich` im Ordner `XO`. `index.html`, `game.js` und `vendor` zusammen belassen. Es ist kein Build erforderlich.

## Gegen den Computer

Drei Schwierigkeitsstufen, X/O-Auswahl und getrennte Statistiken pro Niveau. Nur dieser Modus speichert Einstellungen und Ergebnisse lokal im Browser. Er benötigt keine Netzwerkverbindung und lädt die PeerJS-Bibliothek nicht.

## Mit Freund über einen Einladungslink

1. „Mit Freund“ wählen und „Einladung erstellen“ anklicken.
2. „Link kopieren“ oder die verfügbare Teilen-Funktion verwenden und den Link an den Mitspieler schicken.
3. Die Gastgeberseite geöffnet lassen. Sobald der zweite Browser verbunden ist, beginnt die Runde.
4. Beide müssen einer neuen Runde zustimmen. Die Zeichen wechseln bei jeder Revanche; X beginnt immer.

Ein Raum hat genau zwei Plätze. Der Link enthält eine zufällige Raumkennung und ein zufälliges Zugangsmerkmal im URL-Fragment. Das Fragment wird beim Abruf der Website nicht an GitHub gesendet. Jeder, der den Link hat, kann den freien Platz übernehmen. Der Gastgeber prüft das Zugangsmerkmal sowie Zugreihenfolge, Feld, Rundenkennung und Spielstandversion. Dies ist ein privates Freundesspiel ohne unabhängigen Spielserver; der Gastgeberbrowser verwaltet den Spielstand.

Nach einer Trennung kann der Gast über denselben Link zurückkommen; die Gastgeberseite hält Brett und Ergebnisse im Arbeitsspeicher vor. Beim Schließen oder Neuladen der Gastgeberseite verfällt der Raum. Dann eine neue Einladung erstellen. Freundesspiele werden nicht zu den lokalen Computer-Statistiken addiert.

## Verbindung und Verfügbarkeit

PeerJS 1.5.5 ist mit MIT-Lizenz unter `vendor/` enthalten und wird erst im Freundesmodus geladen. Der öffentliche PeerJS-Server `0.peerjs.com` vermittelt die Verbindung über HTTPS/WSS. Die Bibliothek nutzt standardmäßig Google-STUN sowie die öffentlichen PeerJS-TURN-Dienste zur Herstellung der WebRTC-Datenverbindung. Das Zugangsmerkmal wird als Teil der Verbindungsanfrage über den Vermittlungsdienst übertragen. Dabei kontaktieren die Browser diese Anbieter; sie erhalten Verbindungsdaten wie IP-Adressen und Raum-/Peerkennungen. Kamera und Mikrofon werden nicht angefragt.

Der öffentliche Dienst ist kostenlos und erfordert keine Anmeldung. Seine Verfügbarkeit und die Freigabe von WebRTC im verwendeten Netz können nicht garantiert werden. Bei Fehlern zeigt die Seite eine Meldung und eine Wiederverbindungsmöglichkeit. Firmen-/VPN-/Mobilfunknetze können Einschränkungen verursachen; dann ein anderes Netz probieren. Beide Browser müssen geöffnet und online bleiben.

## Prüfung

Der Computer-Modus wurde mit echten Browserklicks auf Siege, Remis, persistente und getrennte Statistiken, schnelle Neustarts und Zeichenwechsel geprüft. Die perfekte KI wurde gegen alle menschlichen Fortsetzungen ihrer deterministischen Spielstrategie für beide Zeichen sowie in 80 Selbstspielen geprüft. Desktop und 320/390-Pixel-Handyansichten wurden kontrolliert.

Für den Freundesmodus wurden zwei getrennte Browserkontexte verwendet: Einladungslink und Zwischenablage, gemeinsame Brettzustände und Ergebnisse, ungültige Züge und veraltete Versionen, beidseitige Zustimmung zur Revanche, Zeichenwechsel, dritter Teilnehmer, Gast-Neuladen, Verbindungsende und ungültige Links. Wegen Netzbeschränkungen der Bearbeitungsumgebung wurde dafür ein lokaler WebSocket-Testtransport mit derselben PeerJS-Schnittstelle verwendet. Die echte PeerJS-Bibliothek konnte mit einem lokalen Vermittlungsserver Angebote und Antworten austauschen; die WebRTC-ICE-Verbindung sowie der öffentliche Dienst konnten hier nicht vollständig geprüft werden. Der Testtransport gehört nicht zur veröffentlichten Laufzeit.

Nach der Veröffentlichung zusätzlich mit zwei Geräten in unterschiedlichen Netzen prüfen: Einladung öffnen, je einen Zug setzen, Revanche bestätigen und den Gast neu laden. Die Website wird weiterhin über denselben GitHub-Pages-Branch wie Wohnortkarte und Lahntal-Seite veröffentlicht.
