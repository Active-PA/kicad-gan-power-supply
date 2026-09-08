# KiCad-Projektvorlage

Saubere, portable KiCad-Projektvorlage mit hierarchischem Schaltplan und
projektlokalen Bibliotheken. Die Grundstruktur stammt aus der bisherigen
Powertrain-Vorlage; TUWR-Bibliotheken, Submodule, Metadaten und Branding sind
nicht enthalten.

## Struktur

```text
.
|-- kicad_vorlage.kicad_pro
|-- kicad_vorlage.kicad_sch
|-- kicad_vorlage.kicad_pcb
|-- Sheets/
|   |-- HV-Main.kicad_sch
|   `-- LV-Main.kicad_sch
|-- libs/
|   |-- symbols/SamacSys_Parts.kicad_sym
|   |-- footprints/SamacSys_Parts.pretty/
|   `-- 3d/
|-- tools/import_lib.py
|-- import_lib.bat
|-- sym-lib-table
`-- fp-lib-table
```

Die beiden leeren Sheets `HV-Main` und `LV-Main` bilden die vorhandene
hierarchische Grundstruktur ab. Sie können in einem abgeleiteten Projekt
umbenannt, ergänzt oder entfernt werden.

## Vorlage verwenden

1. Repository kopieren oder als Template für ein neues Repository verwenden.
2. Die drei Projektdateien `kicad_vorlage.kicad_*` auf den neuen Projektnamen
   umbenennen.
3. In der `.kicad_pro` den Wert `meta.filename` entsprechend anpassen.
4. Das Projekt über die `.kicad_pro` in KiCad öffnen.

Die Bibliothekstabellen verwenden `${KIPRJMOD}` und funktionieren dadurch ohne
absolute Pfade oder TUWR-Infrastruktur.

## Bauteile importieren

Das Import-Tool übernimmt KiCad-Symbole, Footprints und STEP-Modelle aus
SamacSys-/Mouser-Downloads in die lokalen Bibliotheken.

1. `import_lib.bat` einmal starten. Dabei wird
   `%USERPROFILE%\Downloads\KiCad-Import` angelegt.
2. Importdateien in diesen Ordner legen. Unterstützt werden ZIP-Archive sowie
   `.kicad_sym`, `.kicad_mod`, `.step` und `.stp`.
3. `import_lib.bat` erneut starten.

Erfolgreich verarbeitete Quelldateien erhalten die Endung `.imported`.
ZIP-Dateien ohne unterstützte KiCad-Daten bleiben unverändert. Die Ausgabe ist:

- Symbole: `libs/symbols/SamacSys_Parts.kicad_sym`
- Footprints: `libs/footprints/SamacSys_Parts.pretty/`
- 3D-Modelle: `libs/3d/`

3D-Modellpfade in importierten Footprints werden automatisch als
`${KIPRJMOD}/libs/3d/<Dateiname>` gespeichert.

## Voraussetzungen

- KiCad 9 oder neuer
- Python 3 im `PATH` für das Import-Tool
