#!/usr/bin/env python3
import zipfile
from pathlib import Path
import shutil
import re
import tempfile

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMPORT_INBOX = Path.home() / "Downloads" / "KiCad-Import"

LIB_ROOT = PROJECT_ROOT / "libs"
SYM_DIR = LIB_ROOT / "symbols"
FP_ROOT = LIB_ROOT / "footprints"
STEP_DIR = LIB_ROOT / "3d"

MASTER_SYM_LIB = SYM_DIR / "SamacSys_Parts.kicad_sym"
MASTER_FP_DIR = FP_ROOT / "SamacSys_Parts.pretty"
SUPPORTED_ARCHIVE_SUFFIXES = (".kicad_sym", ".kicad_mod", ".step", ".stp")


SYM_DIR.mkdir(parents=True, exist_ok=True)
FP_ROOT.mkdir(parents=True, exist_ok=True)
MASTER_FP_DIR.mkdir(parents=True, exist_ok=True)
STEP_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Symbol-Merge-Helfer
# ---------------------------------------------------------------------------

SYMBOL_NAME_RE = re.compile(r'\(symbol\s+"([^"]+)"')

def ensure_master_sym_lib():
    """Master-Symbolbibliothek anlegen, falls noch nicht vorhanden."""
    if not MASTER_SYM_LIB.exists():
        MASTER_SYM_LIB.write_text('(kicad_symbol_lib (version 20211014) (generator "import_lib")\n)\n', encoding="utf-8")

def load_master_symbols():
    """Alle bereits vorhandenen Symbol-Namen aus der Master-Lib auslesen."""
    if not MASTER_SYM_LIB.exists():
        return set(), ['(kicad_symbol_lib (version 20211014) (generator "import_lib")\n', ')\n']

    text = MASTER_SYM_LIB.read_text(encoding="utf-8")
    existing_names = set(SYMBOL_NAME_RE.findall(text))
    lines = text.splitlines(keepends=True)
    return existing_names, lines

def extract_symbol_blocks(text: str):
    """Alle (symbol ...) Blöcke aus einem .kicad_sym-Text extrahieren."""
    symbols = []
    i = 0
    while True:
        start = text.find("(symbol ", i)
        if start == -1:
            break
        depth = 0
        j = start
        end = None
        while j < len(text):
            ch = text[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
            j += 1
        if end is None:
            # Ungültige Datei, abbrechen
            break
        symbols.append(text[start:end])
        i = end
    return symbols

def merge_symbols_from_file(sym_file: Path):
    """Symbole aus einer .kicad_sym-Datei in die Master-Lib mergen (ohne Duplikate)."""
    ensure_master_sym_lib()
    existing_names, master_lines = load_master_symbols()
    src_text = sym_file.read_text(encoding="utf-8")
    blocks = extract_symbol_blocks(src_text)

    if not blocks:
        print(f"    (i) Keine (symbol ...) Blöcke in {sym_file.name} gefunden.")
        return

    new_blocks = []
    for block in blocks:
        m = SYMBOL_NAME_RE.search(block)
        if not m:
            continue
        name = m.group(1)
        if name in existing_names:
            print(f"    (i) Symbol '{name}' bereits vorhanden – überspringe.")
            continue
        existing_names.add(name)
        new_blocks.append(block)

    if not new_blocks:
        print("    (i) Keine neuen Symbole zum Hinzufügen.")
        return

    # Neue Symbole vor der letzten schließenden Klammer einfügen
    # Wir gehen davon aus, dass die letzte Zeile nur ')' ist.
    if master_lines and master_lines[-1].strip() == ")":
        insert_index = len(master_lines) - 1
    else:
        insert_index = len(master_lines)

    for block in new_blocks:
        master_lines.insert(insert_index, "  " + block.replace("\n", "\n  ").rstrip() + "\n")
        insert_index += 1

    MASTER_SYM_LIB.write_text("".join(master_lines), encoding="utf-8")
    print(f"    (+) {len(new_blocks)} neue Symbole nach {MASTER_SYM_LIB.name} gemerged.")


# ---------------------------------------------------------------------------
# Footprint & 3D Helper
# ---------------------------------------------------------------------------

def copy_if_new(src: Path, dst_dir: Path, kind: str):
    """Datei nur kopieren, wenn sie im Zielverzeichnis noch nicht existiert."""
    dst = dst_dir / src.name
    if dst.exists():
        print(f"    (i) {kind} {dst.name} existiert bereits – überspringe.")
    else:
        shutil.copy2(src, dst)
        print(f"    (+) {kind} -> {dst.name}")

MODEL_RE = re.compile(r'\(model\s+("?)([^"\s)]+\.(?:stp|step))\1', re.IGNORECASE)

def fix_3d_paths_in_footprints():
    """Setzt 3D-Modellpfade relativ zum Projekt, damit das Repo portabel bleibt."""
    for fp_file in MASTER_FP_DIR.glob("*.kicad_mod"):
        text = fp_file.read_text(encoding="utf-8")

        def repl(match):
            orig_path = match.group(2)
            fname = Path(orig_path).name
            # WICHTIG: KEINE schließende Klammer hier!
            return f'(model "${{KIPRJMOD}}/libs/3d/{fname}"'

        new_text = MODEL_RE.sub(repl, text)

        if new_text != text:
            fp_file.write_text(new_text, encoding="utf-8")
            print(f"    (3D) Pfade in {fp_file.name} angepasst.")

# ---------------------------------------------------------------------------
# ZIP & Einzeldatei-Handling
# ---------------------------------------------------------------------------

def handle_zip(zip_path: Path):
    with zipfile.ZipFile(zip_path) as z:
        members = [
            member for member in z.namelist()
            if Path(member).name.lower().endswith(SUPPORTED_ARCHIVE_SUFFIXES)
        ]
        if not members:
            print(f"[ZIP] Keine KiCad-Daten, überspringe: {zip_path.name}")
            return False

        print(f"[ZIP] Importiere: {zip_path.name}")
        with tempfile.TemporaryDirectory(prefix="kicad-import-") as temp_dir:
            extracted = []
            for index, member in enumerate(members):
                name = Path(member).name
                target_dir = Path(temp_dir) / str(index)
                target_dir.mkdir()
                target = target_dir / name
                with z.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted.append(target)

            for temp_file in extracted:
                lower = temp_file.name.lower()
                if lower.endswith(".kicad_sym"):
                    print(f"    [SYM] Merging aus {temp_file.name}")
                    merge_symbols_from_file(temp_file)
                elif lower.endswith(".kicad_mod"):
                    copy_if_new(temp_file, MASTER_FP_DIR, "Footprint")
                else:
                    copy_if_new(temp_file, STEP_DIR, "3D-Model")

    # ZIP als verarbeitet markieren
    zip_path.rename(zip_path.with_suffix(zip_path.suffix + ".imported"))
    return True


def handle_file(f: Path):
    lower = f.name.lower()
    if lower.endswith(".kicad_sym"):
        print(f"[SYM] Einzeldatei: {f.name}")
        merge_symbols_from_file(f)
        f.rename(f.with_suffix(f.suffix + ".imported"))

    elif lower.endswith(".kicad_mod"):
        print(f"[FP] Einzeldatei: {f.name}")
        copy_if_new(f, MASTER_FP_DIR, "Footprint")
        f.rename(f.with_suffix(f.suffix + ".imported"))

    elif lower.endswith((".step", ".stp")):
        print(f"[3D] Einzeldatei: {f.name}")
        copy_if_new(f, STEP_DIR, "3D-Model")
        f.rename(f.with_suffix(f.suffix + ".imported"))


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("📥 SamacSys/Mouser Importer")
    print(f"Projekt   : {PROJECT_ROOT}")
    print(f"Importordner: {IMPORT_INBOX}")

    if not IMPORT_INBOX.exists():
        IMPORT_INBOX.mkdir(parents=True)
        print("Importordner wurde angelegt. Dateien dort ablegen und das Tool erneut starten.")
        return

    # ZIP-Dateien im Importordner
    for zip_path in IMPORT_INBOX.glob("*.zip"):
        if ".imported" in "".join(zip_path.suffixes):
            continue
        handle_zip(zip_path)

    # Einzelne Dateien (.kicad_sym, .kicad_mod, .step)
    for f in IMPORT_INBOX.iterdir():
        if f.is_file() and not "".join(f.suffixes).endswith(".imported"):
            handle_file(f)

    # 3D-Pfade in allen Footprints korrigieren
    fix_3d_paths_in_footprints()

    print("✅ Fertig! Symbole in SamacSys_Parts.kicad_sym, Footprints in SamacSys_Parts.pretty, 3D in libs/3d.")


if __name__ == "__main__":
    main()
