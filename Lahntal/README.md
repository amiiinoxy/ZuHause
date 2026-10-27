# Unteres Lahntal – QGIS-Probeklausur 2026

## Ergebnisse öffnen

- **Lahntal_A2.pdf**: fertige einseitige A2-Karte, quer, 594 × 420 mm, Maßstab 1:65 000. Beim Drucken „Tatsächliche Größe“ / 100 % wählen.
- **Lahntal.qgz**: bearbeitbares QGIS-Projekt. Den gesamten ZIP-Inhalt entpacken und anschließend diese Datei öffnen. `daten`, `fotos` und `symbole` müssen zusammen mit der Projektdatei im gleichen übergeordneten Ordner bleiben. Ein Internetzugriff ist zur Anzeige nicht erforderlich.
- **Quellen_und_Methodik.pdf** / **QUELLEN_UND_METHODIK.md**: vollständige Quellen, Lizenzen, Vorgehensweise und fachliche Grenzen.
- **recherche/Ausgewaehlte_Zufluesse.csv**: ausgewählte Gewässer mit Kennzahlen und Längen.
- **recherche/Endvalidierung.json**: ermittelte Objektzahlen und Auswahlwerte.

Die Prüfungskennziffer wurde aus der Nutzerantwort als **204** übernommen. Der Name wird entsprechend der Aufgabenstellung nicht angegeben. Die Rechnerkennung ist der tatsächliche Hostname der Bearbeitungsumgebung. Die Ernennung zur Flusslandschaft 2026 ist ausdrücklich ein fiktives Szenario aus der Aufgabenstellung.

## Inhalt

Rhein und Lahn, 40 direkte Zuflüsse > 1 km, Fließpfeile, Autobahnen A3/A48, Bundes- und Landesstraßen, hervorgehobene Ortslagen bis 500 m von den ausgewählten Gewässern, Lahnwanderweg, zehn Fotostandorte mit zugehöriger Fotoleiste, Wald, Landwirtschaft und die im Ausschnitt liegenden Kreise bzw. Koblenz als kreisfreie Stadt.

Das in der XLSX als DLM50 bezeichnete WFS-Angebot liefert tatsächlich das genauere Basis-DLM RLP. Dieses wurde für Landwirtschaft und die Lage der Straßen in RLP eingesetzt und korrekt bezeichnet. DLM250 liefert Wald und ergänzende Straßen am hessischen Kartenrand. Die Prüfung der Fotolizenzen hat mehrere Abweichungen von der Excel-Tabelle ergeben; die Karte verwendet die auf Wikimedia verifizierten Lizenzen.

Der Gewässer-WFS hat kein separates Verrohrungsattribut. Der direkte Anschluss wird aus dem amtlich kartierten Fließgewässernetz ermittelt; einzelne kurze verrohrte Mündungsstücke sind damit nicht gesondert überprüfbar. Diese Einschränkung ist im Methodennachweis offengelegt.

## Erneut exportieren

Erforderlich sind QGIS/PyQGIS 3.40 oder kompatibel, DejaVu Sans und Ghostscript. Die Daten sind bereits enthalten. Unter der verwendeten Linux-Umgebung:

```sh
QT_QPA_PLATFORM=offscreen /usr/bin/python3 skripte/karte_erstellen.py
python skripte/nachweise_erstellen.py
```

Der zweite Befehl benötigt ReportLab. Der erste Befehl erzeugt `daten/Kartendaten.gpkg`, das QGIS-Projekt und die A2-PDF erneut. Er überschreibt diese generierten Ergebnisse. Die Originaleingaben und heruntergeladenen Quell-Geometrien bleiben bestehen. Der unmittelbare QGIS-PDF-Export wird unter `recherche/Lahntal_A2_Direktexport.pdf` abgelegt; die finale PDF enthält weiterhin Vektorkartographie, die eingebetteten Fotos sind für 300 dpi optimiert.

`skripte/internet_pruefen.py` ist eine optionale, rein lesende Dienstprüfung. Die bei Arbeitsbeginn bestehende Netzwerksperre wurde im Verlauf aufgehoben; sämtliche für das Ergebnis benötigten Daten und Fotos wurden anschließend erfolgreich abgerufen.

Das ursprüngliche Git-Repository wurde nicht verändert.
