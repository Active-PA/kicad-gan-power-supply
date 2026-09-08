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
|-- fp-lib-table
`-- meta/info.html
```

Die beiden leeren Sheets `HV-Main` und `LV-Main` bilden die vorhandene
hierarchische Grundstruktur ab. Sie können in einem abgeleiteten Projekt
umbenannt, ergänzt oder entfernt werden.

## Empfohlen: Projekt mit Vorlagen-Historie anlegen

Wenn spätere Änderungen dieser Vorlage in ein bestehendes Projekt übernommen
werden sollen, muss das neue Projekt die Git-Historie der Vorlage behalten.
Dafür wird die Vorlage geklont und anschließend als `upstream` eingetragen.

```powershell
git clone https://github.com/Active-PA/kicad_vorlage.git mein-projekt
Set-Location mein-projekt

# Die Vorlage bleibt als Quelle für spätere Aktualisierungen erhalten.
git remote rename origin upstream

# Das neue, leere GitHub-Repository des konkreten Projekts eintragen.
git remote add origin https://github.com/Active-PA/mein-projekt.git
```

Danach das Projekt im KiCad Project Manager über **Datei -> Speichern unter**
unter dem endgültigen Namen speichern, zum Beispiel `active_pa_v2`. Die alten
`kicad_vorlage.kicad_*`-Dateien anschließend entfernen und die Umbenennung als
ersten projektspezifischen Commit speichern:

```powershell
git add -A
git commit -m "Projekt aus KiCad-Vorlage anlegen"
git push -u origin main
```

Spätere Änderungen aus der Vorlage werden so übernommen:

```powershell
git fetch upstream
git merge upstream/main
```

Git erkennt die umbenannten Projektdateien normalerweise als Renames und führt
Änderungen aus der Vorlage nach. Wenn dieselben KiCad-Projektdateien sowohl in
der Vorlage als auch im konkreten Projekt stark geändert wurden, können normale
Merge-Konflikte entstehen. Werkzeuge, Bibliotheksstruktur, `.gitignore` und
Dokumentation lassen sich in der Regel konfliktarm aktualisieren.

Ein echter GitHub-Fork funktioniert nach demselben Prinzip. Ein normaler Clone
mit `upstream` und einem eigenen `origin` ist für mehrere unterschiedliche
Hardwareprojekte meist flexibler.

## Alternative: native KiCad-Vorlage ohne Git-Verknüpfung

Der Ordnername `kicad_vorlage`, die drei Projektdateien und der interne
Projektname stimmen überein. Dadurch kann KiCad sie beim Erzeugen eines neuen
Projekts automatisch auf den gewünschten Projektnamen umbenennen.

1. Das Repository in einen Ordner für eigene KiCad-Vorlagen klonen. Der
   Repository-Ordner muss dabei `kicad_vorlage` heißen.
2. In KiCad unter **Einstellungen -> Pfade konfigurieren** den Pfad
   `KICAD_USER_TEMPLATE_DIR` auf den übergeordneten Vorlagenordner setzen.
3. **Datei -> Neues Projekt aus Vorlage** öffnen und diese Vorlage auswählen.
4. Zielordner und neuen Projektnamen eingeben, zum Beispiel `active_pa_v2`.

KiCad kopiert die Vorlage und erzeugt dabei automatisch
`active_pa_v2.kicad_pro`, `active_pa_v2.kicad_sch` und
`active_pa_v2.kicad_pcb`. Der Ordner `meta` wird nicht in das neue Projekt
kopiert.

Das Repository kann auch normal kopiert werden. Dann müssen die drei
Dateien `kicad_vorlage.kicad_*` gemeinsam umbenannt und der Wert
`meta.filename` in der `.kicad_pro` angepasst werden. Der native
KiCad-Vorlagenweg ist weniger fehleranfällig, ermöglicht aber kein späteres
`git merge upstream/main`.

Die Bibliothekstabellen verwenden `${KIPRJMOD}` und funktionieren dadurch ohne
absolute Pfade oder TUWR-Infrastruktur.

## Warum kein Git-Submodul für das Projekt selbst?

Ein Submodul eignet sich nur, wenn dieses Vorlagen-Repository in einem anderen
Repository als zentral aktualisierbare Vorlage mitgeführt werden soll, etwa
unter `templates/kicad_vorlage`. Das eigentliche KiCad-Projekt sollte daraus
kopiert beziehungsweise über **Neues Projekt aus Vorlage** erzeugt werden. Es
sollte nicht selbst im Submodul bearbeitet werden.

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
