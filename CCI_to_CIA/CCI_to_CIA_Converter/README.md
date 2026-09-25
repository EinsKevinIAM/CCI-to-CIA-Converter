# CCI → CIA Converter für Windows

Eine einfache Windows-GUI um Nintendo-3DS-CCI/3DS-Dateien über die
offizielle `3dsconv`-Python-Implementierung in CIA umzuwandeln.

## Projektstruktur

```text
CCI_to_CIA_Converter/
├─ cci_to_cia_gui.py
├─ build.bat
├─ requirements.txt
├─ README.md
└─ vendor/
   └─ 3dsconv.py
```

## 1. Voraussetzungen

- Windows 10/11
- Python 3
- Internetzugang beim ersten Build
- die offizielle `3dsconv.py` aus dem Projekt `ihaveamac/3dsconv`

Die aktuelle 3dsconv-Version ist 4.2. Das Originalprojekt beschreibt die
Umwandlung von CCI/3DS nach CIA und nennt `pyaes` als Abhängigkeit für
verschlüsselte Dateien.

## 2. 3dsconv.py einfügen

Lade die offizielle Version aus:

https://github.com/ihaveamac/3dsconv

und lege `3dsconv.py` hier ab:

```text
vendor\3dsconv.py
```

## 3. EXE bauen

Doppelklick auf:

```text
build.bat
```

Das Skript installiert die Python-Abhängigkeiten und erstellt mit PyInstaller
eine einzelne Windows-EXE.

Danach liegt sie hier:

```text
dist\CCI_to_CIA_Converter.exe
```

Die EXE benötigt Python auf dem Ziel-PC nicht.

## 4. Verwendung

1. `CCI_to_CIA_Converter.exe` starten.
2. Eine `.cci` oder `.3ds` Datei auswählen.
3. Ausgabeordner auswählen.
4. `Konvertieren` drücken.

Die erzeugte Datei erhält automatisch den ursprünglichen Dateinamen mit
`.cia`.

## Verschlüsselte Dateien

Nicht jede CCI kann ohne zusätzliche Schlüssel konvertiert werden.
3dsconv dokumentiert, dass bei Original-NCCH-Verschlüsselung ein passender
ARM9-BootROM-Dump (`boot9.bin` bzw. `boot9_prot.bin`) benötigt werden kann.

Lege einen benötigten `boot9`-Dump gemäß der Dokumentation der verwendeten
3dsconv-Version an den dort beschriebenen Ort. Die GUI verändert oder
erzeugt keine solchen Schlüssel.

## Rechtlicher Hinweis

Verwende das Programm nur mit Dateien, zu deren Nutzung und Konvertierung
du berechtigt bist. Die GUI selbst enthält keine Nintendo-ROMs,
Schlüssel oder sonstige Spieldaten.

## Lizenz

Die GUI dieses Projekts ist von mir als Beispielcode erstellt.
`3dsconv.py` unterliegt seiner eigenen Lizenz. Beachte die Lizenzhinweise
des Originalprojekts.


## Falls beim Build "IndentationError" erscheint

Falls du eine ältere ZIP-Version verwendet hast und folgende Meldung bekommst:

```text
IndentationError: expected an indented block after function definition
```

verwende bitte die korrigierte Version aus diesem Projekt. In `cci_to_cia_gui.py`
muss `_enable_drop()` mindestens `pass` enthalten.

## Python 3.14

Der Build verwendet bewusst:

```text
py -3 -m PyInstaller
```

statt eines direkten Aufrufs von `pyinstaller`. Dadurch ist es egal, ob der
Python-Scripts-Ordner bereits in `PATH` eingetragen ist.


## Mehrere Dateien / Ordner

Mit der aktuellen GUI kannst du über **„Ordner auswählen…“** einen Ordner
auswählen. Alle `.cci` und `.3ds` Dateien direkt in diesem Ordner werden
automatisch gefunden und nacheinander konvertiert.

Unterordner werden nicht durchsucht.

Die CIA-Dateien werden standardmäßig im ausgewählten Ausgabeordner abgelegt.
Die ursprünglichen Dateinamen bleiben erhalten, lediglich die Endung wird
von `.cci`/`.3ds` auf `.cia` geändert.

Die Fortschrittsanzeige zeigt den Gesamtfortschritt des Batch-Vorgangs.
Fehlgeschlagene Dateien werden protokolliert und die übrigen Dateien werden
weiter verarbeitet.
