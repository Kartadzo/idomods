#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warstwa logiki edytora bazy summonFeed — bez tkintera, więc testowalna headless.

Odpowiada za: odczyt istniejących elementów, wykrywanie kolizji nazw, złożenie treści
plików JSON/XSL, planowanie zapisu (z wykryciem duplikatów), kopię zapasową, dopisanie
wpisów do rejestrów i uruchomienie walidatora.

GUI (``summonFeed_editor.py``) nie zna układu katalogów — pyta o wszystko ten moduł.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')

# <xsl:variable name="x" select="'v'"/>  →  <xsl:variable name="x">v</xsl:variable>
# Generator podmienia configVary wyłącznie w drugiej formie; deklaracja z select=
# jest po cichu ignorowana i parametr zawsze bierze wartość domyślną.
VAR_SELECT_RE = re.compile(
    r"""<xsl:variable\s+name\s*=\s*(?P<q>["'])(?P<name>[^"']+)(?P=q)\s+"""
    r"""select\s*=\s*(?P<sq>["'])(?P<value>.*?)(?P=sq)\s*/>""",
    re.DOTALL)

# domyślne punkty wstawienia nowej struktury (jak w google.json / samba.json)
DEFAULT_INSERTION_POINTS = [
    {"template": "product", "context": "product"},
    {"template": "productSizeMatter", "context": "size"},
]


@dataclass
class PlannedWrite:
    """Jeden plik do zapisania. 'status' rozstrzyga, czy trafi na dysk bez pytania."""
    path: Path
    content: str
    label: str                      # co to jest, np. "parameters_templates/title.json"
    status: str = 'new'             # new | identical | conflict
    existing: Optional[str] = None  # dotychczasowa treść (dla 'identical'/'conflict')
    overwrite: bool = True          # decyzja użytkownika dla 'conflict'


@dataclass
class WritePlan:
    writes: List[PlannedWrite] = field(default_factory=list)
    warnings: List[Tuple[str, Dict[str, str]]] = field(default_factory=list)

    @property
    def conflicts(self) -> List[PlannedWrite]:
        return [w for w in self.writes if w.status == 'conflict']

    def to_apply(self) -> List[PlannedWrite]:
        """Pliki, które faktycznie trafią na dysk po uwzględnieniu decyzji."""
        return [w for w in self.writes
                if w.status == 'new' or (w.status == 'conflict' and w.overwrite)]


class EditorModel:
    """Operacje na bazie summonFeed. Ścieżki liczone względem katalogu tego pliku."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.parameters_path = self.base_path / "parameters_templates"
        self.structures_path = self.base_path / "structure_templates"
        self.variables_path = self.base_path / "variables"
        self.helpers_path = self.base_path / "helpers"
        self.backup_path = self.base_path / "_backup"
        self.lang_path = self.base_path / "lang"

    # ------------------------------------------------------------------
    #  ODCZYT ISTNIEJĄCEJ BAZY
    # ------------------------------------------------------------------

    def _read_json(self, path: Path) -> Dict:
        return json.loads(path.read_text(encoding='utf-8'))

    def list_parameters(self) -> List[str]:
        return sorted(p.stem for p in self.parameters_path.glob("*.json")
                      if not p.name.startswith('_'))

    def list_structures(self) -> List[str]:
        """Nazwy struktur tak, jak zapisane w polu 'name' (np. 'Google'), nie nazwy plików."""
        names = []
        for p in sorted(self.structures_path.glob("*.json")):
            if p.name.startswith('_'):
                continue
            try:
                names.append(self._read_json(p).get('name', p.stem))
            except (json.JSONDecodeError, OSError):
                names.append(p.stem)
        return names

    def list_global_variables(self) -> List[str]:
        reg = self._registry(self.variables_path / "_registry.json")
        return sorted(n for n, meta in reg.items()
                      if isinstance(meta, dict) and meta.get('scope') == 'global')

    def list_exclusive_groups(self) -> List[str]:
        groups = set()
        for p in self.parameters_path.glob("*.json"):
            if p.name.startswith('_'):
                continue
            try:
                group = self._read_json(p).get('exclusiveGroup')
            except (json.JSONDecodeError, OSError):
                continue
            if group:
                groups.add(group)
        return sorted(groups)

    def list_contexts(self) -> List[str]:
        return ['product', 'size', 'feed']

    def _registry(self, path: Path) -> Dict:
        if not path.exists():
            return {}
        try:
            data = self._read_json(path)
        except (json.JSONDecodeError, OSError):
            return {}
        return {k: v for k, v in data.items() if not k.startswith('_')}

    # ------------------------------------------------------------------
    #  WCZYTANIE KONFIGURACJI DO AKTUALIZACJI
    # ------------------------------------------------------------------

    def detect_kind(self, json_path: Path) -> Optional[str]:
        """'structure' | 'parameter' | None — rozpoznanie po zawartości, nie po katalogu."""
        try:
            data = self._read_json(Path(json_path))
        except (json.JSONDecodeError, OSError):
            return None
        if 'insertionPoints' in data:
            return 'structure'
        if data.get('context') in self.list_contexts():
            return 'parameter'
        return None

    def load_form(self, json_path: Path) -> Dict:
        """Wczytaj plik .json (i .xsl obok) do słownika wartości formularza."""
        json_path = Path(json_path)
        data = self._read_json(json_path)
        kind = self.detect_kind(json_path)
        xsl_path = json_path.with_suffix('.xsl')
        xsl = xsl_path.read_text(encoding='utf-8') if xsl_path.exists() else ''

        form = {
            'kind': kind,
            'original_name': data.get('name', json_path.stem),
            'source_path': json_path,
            'name': data.get('name', json_path.stem),
            'description': data.get('description', ''),
            'description_pl': data.get('description_pl', ''),
            'output': data.get('output', ''),
            'notes': data.get('notes', ''),
            'xsl': xsl,
        }

        if kind == 'parameter':
            config_rows, inline_vars = self._load_config_vars(data)
            form.update({
                'structure': list(data.get('structure', [])),
                'context': data.get('context', 'product'),
                'exclusiveGroup': data.get('exclusiveGroup', '') or '',
                'exclusiveDefaultFor': list(data.get('exclusiveDefaultFor', [])),
                'xpathCandidates': list(data.get('xpathCandidates', [])),
                'parameterContexts': list(data.get('parameterContexts', [])),
                'globals': list(data.get('globals', [])),
                'configVars': config_rows,
                'inlineCreateVars': inline_vars,
                'helpers': self._load_helpers(data),
            })
        return form

    def _load_config_vars(self, data: Dict) -> Tuple[List[Dict], List[str]]:
        """(wiersze formularza, createVars deklarowane inline).

        createVar bez pliku w ``variables/`` należy do parametru *legacy* — jest
        deklarowany wprost w jego ``.xsl``. Taki wpis nie może trafić do formularza jako
        „zmienna wydzielona", bo zapis utworzyłby pusty plik i wpis w rejestrze, przez co
        generator uznałby parametr za zmigrowany i przestał używać deklaracji inline."""
        var_reg = self._registry(self.variables_path / "_registry.json")
        rows = []
        for var in data.get('configVars', []):
            rows.append({
                'name': var.get('name', ''),
                'default': var.get('default', ''),
                'delimeter': var.get('delimeter', ''),
                'extract': False, 'scope': 'local', 'order': '', 'uses': [], 'xsl': '',
            })
        seen = {r['name'] for r in rows}
        inline: List[str] = []
        for cv in data.get('createVars', []):
            xsl_file = self.variables_path / f"{cv}.xsl"
            if not xsl_file.exists():
                inline.append(cv)
                continue
            meta = var_reg.get(cv, {})
            row = {
                'name': cv, 'default': '', 'delimeter': '',
                'extract': True,
                'scope': 'global' if meta.get('scope') == 'global' else 'local',
                'order': str(meta.get('order', '')) if meta.get('order') is not None else '',
                'uses': list(meta.get('uses', [])),
                'xsl': xsl_file.read_text(encoding='utf-8'),
            }
            if cv in seen:  # ta sama nazwa jako configVar i createVar → jeden wiersz
                for r in rows:
                    if r['name'] == cv:
                        r.update({k: v for k, v in row.items() if k != 'name'})
            else:
                rows.append(row)
        return rows, inline

    def _load_helpers(self, data: Dict) -> List[Dict]:
        reg = self._registry(self.helpers_path / "_registry.json")
        rows = []
        for name in data.get('helpers', []):
            meta = reg.get(name, {})
            xsl_file = self.helpers_path / f"{name}.xsl"
            rows.append({
                'name': name,
                'xsl': xsl_file.read_text(encoding='utf-8') if xsl_file.exists() else '',
                'uses': list(meta.get('uses', [])),
                'globals': list(meta.get('globals', [])),
            })
        return rows

    # ------------------------------------------------------------------
    #  NAZWY I KOLIZJE
    # ------------------------------------------------------------------

    def file_stem(self, kind: str, name: str) -> str:
        """Nazwa pliku z pola 'name'. Struktury zapisane są małymi literami
        ('Google' → google.json), parametry dokładnie tak, jak w polu 'name'
        (walidator wymaga zgodności name == nazwa pliku)."""
        return name.lower() if kind == 'structure' else name

    def target_dir(self, kind: str) -> Path:
        return self.structures_path if kind == 'structure' else self.parameters_path

    def name_conflict(self, kind: str, name: str,
                      original_name: Optional[str] = None) -> Optional[Path]:
        """Ścieżka kolidującego pliku albo None.

        Przy aktualizacji kolizją jest wyłącznie zmiana nazwy na inną, już zajętą —
        nadpisanie własnego pliku kolizją nie jest."""
        if not name:
            return None
        if original_name and name == original_name:
            return None
        path = self.target_dir(kind) / f"{self.file_stem(kind, name)}.json"
        return path if path.exists() else None

    def validate_name(self, name: str) -> Optional[str]:
        """Klucz komunikatu o błędzie nazwy albo None."""
        if not name.strip():
            return 'name_required'
        if not NAME_RE.match(name.strip()):
            return 'name_invalid'
        return None

    # ------------------------------------------------------------------
    #  NORMALIZACJA XSL
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_variable_decls(xsl: str) -> str:
        """Zamień <xsl:variable name="x" select="'v'"/> na <xsl:variable name="x">v</xsl:variable>.

        Apostrofy wokół literału znikają — wartość staje się treścią elementu.
        Deklaracje z wyrażeniem XPath (bez apostrofów, np. select="../@id") zostają
        nietknięte: ich wartość nie jest stałą, więc treść elementu by ją zepsuła."""
        def repl(m):
            value = m.group('value')
            if not (value.startswith("'") and value.endswith("'") and len(value) >= 2):
                return m.group(0)   # wyrażenie XPath, nie literał — nie ruszamy
            return f'<xsl:variable name="{m.group("name")}">{value[1:-1]}</xsl:variable>'
        return VAR_SELECT_RE.sub(repl, xsl)

    def missing_templates(self, xsl: str,
                          insertion_points: Optional[List[Dict]] = None) -> List[Dict]:
        """Punkty wstawienia, dla których szkielet nie ma pustego named template."""
        points = insertion_points or DEFAULT_INSERTION_POINTS
        missing = []
        for point in points:
            pattern = (r'<xsl:template[^>]*name="' + re.escape(point['template'])
                       + r'"[^>]*>\s*</xsl:template>')
            if not re.search(pattern, xsl):
                missing.append(point)
        return missing

    # ------------------------------------------------------------------
    #  SKŁADANIE TREŚCI PLIKÓW
    # ------------------------------------------------------------------

    @staticmethod
    def _dump(data: Dict) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    def build_structure_json(self, form: Dict) -> str:
        name = form['name'].strip()
        stem = self.file_stem('structure', name)
        return self._dump({
            "name": name,
            "description": form.get('description', ''),
            "description_pl": form.get('description_pl', ''),
            "output": form.get('output') or 'rss/channel/item',
            "context": "feed",
            "xpathCandidates": ["/offer/products/product"],
            "parameterContexts": [],
            "configVars": [],
            "helpers": [],
            "insertionPoints": DEFAULT_INSERTION_POINTS,
            "defaultXslt": f"summonFeed/structure_templates/{stem}.xsl",
            "notes": form.get('notes', ''),
        })

    def build_parameter_json(self, form: Dict) -> str:
        name = form['name'].strip()
        rows = [r for r in form.get('configVars', []) if r.get('name', '').strip()]
        config_vars = []
        # createVars deklarowane inline w .xsl (parametr legacy) zostają nietknięte
        create_vars = [v for v in form.get('inlineCreateVars', [])]
        for row in rows:
            if row.get('extract'):
                if row['name'].strip() not in create_vars:
                    create_vars.append(row['name'].strip())
                # zmienna wydzielona do variables/ nadal bywa configVarem — gdy ma default
                if row.get('default', '') != '':
                    config_vars.append(self._config_var_entry(row))
            else:
                config_vars.append(self._config_var_entry(row))

        data = {
            "name": name,
            "description": form.get('description', ''),
            "description_pl": form.get('description_pl', ''),
            "structure": list(form.get('structure', [])),
            "output": form.get('output') or name,
            "context": form.get('context', 'product'),
        }
        if form.get('exclusiveGroup', '').strip():
            data["exclusiveGroup"] = form['exclusiveGroup'].strip()
            data["exclusiveDefaultFor"] = list(form.get('exclusiveDefaultFor', []))
        data.update({
            "xpathCandidates": list(form.get('xpathCandidates', [])),
            "parameterContexts": list(form.get('parameterContexts', [])),
            "configVars": config_vars,
            "createVars": create_vars,
            "helpers": [h['name'].strip() for h in form.get('helpers', [])
                        if h.get('name', '').strip()],
            "globals": list(form.get('globals', [])),
            "notes": form.get('notes', ''),
        })
        return self._dump(data)

    @staticmethod
    def _config_var_entry(row: Dict) -> Dict:
        entry = {"name": row['name'].strip(), "default": row.get('default', '')}
        if row.get('delimeter', ''):
            entry["delimeter"] = row['delimeter']
        return entry

    # ------------------------------------------------------------------
    #  REJESTRY — dopisanie wpisu z zachowaniem formatowania pliku
    # ------------------------------------------------------------------

    def registry_entry_text(self, path: Path, key: str, value: Dict) -> Optional[str]:
        """Nowa treść pliku rejestru z dopisanym/podmienionym wpisem.
        None, gdy rejestr już zawiera wpis o tym znaczeniu.

        Porównanie jest semantyczne, nie tekstowe: wpisy w rejestrach są wyrównane
        spacjami do kolumn i przepisanie ich tylko dlatego, że mój `json.dumps` formatuje
        inaczej, kasowałoby to wyrównanie przy każdej edycji."""
        line = f'  "{key}": ' + json.dumps(value, ensure_ascii=False, separators=(', ', ': '))

        if not path.exists():
            return "{\n" + line + "\n}\n"

        if self._registry(path).get(key) == value:
            return None

        text = path.read_text(encoding='utf-8')
        existing = re.search(r'^[ \t]*"' + re.escape(key) + r'"\s*:.*$', text, re.MULTILINE)
        if existing:
            old = existing.group(0)
            trailing = ',' if old.rstrip().endswith(',') else ''
            new_line = line + trailing
            if old.strip() == new_line.strip():
                return None
            return text[:existing.start()] + new_line + text[existing.end():]

        close = text.rstrip().rfind('}')
        if close == -1:
            return None
        head = text[:close].rstrip()
        if not head.endswith(','):
            head += ','
        return head + "\n" + line + "\n}\n"

    # ------------------------------------------------------------------
    #  PLAN ZAPISU
    # ------------------------------------------------------------------

    def _add(self, plan: WritePlan, path: Path, content: str, label: str) -> None:
        if path.exists():
            existing = path.read_text(encoding='utf-8')
            # Pole tekstowe tkintera zawsze oddaje treść zakończoną nową linią, a spora
            # część plików .xsl w repo jej nie ma. Różnica wyłącznie w końcowych białych
            # znakach to nie zmiana treści — inaczej samo otwarcie parametru w edytorze
            # zgłaszałoby konflikt.
            if existing == content or existing.rstrip() == content.rstrip():
                plan.writes.append(PlannedWrite(path, existing, label, 'identical', existing))
            else:
                plan.writes.append(PlannedWrite(path, content, label, 'conflict', existing))
        else:
            plan.writes.append(PlannedWrite(path, content, label, 'new'))

    def plan_writes(self, form: Dict) -> WritePlan:
        """Zbierz wszystkie pliki, które trzeba zapisać, wraz z konfliktami i ostrzeżeniami."""
        plan = WritePlan()
        kind = form['kind']
        name = form['name'].strip()
        stem = self.file_stem(kind, name)
        target = self.target_dir(kind)
        xsl = self.normalize_variable_decls(form.get('xsl', ''))

        if kind == 'structure':
            self._add(plan, target / f"{stem}.json", self.build_structure_json(form),
                      f"structure_templates/{stem}.json")
            self._add(plan, target / f"{stem}.xsl", xsl, f"structure_templates/{stem}.xsl")
            for point in self.missing_templates(xsl):
                plan.warnings.append(('warn_missing_template', dict(point)))
            return plan

        self._add(plan, target / f"{stem}.json", self.build_parameter_json(form),
                  f"parameters_templates/{stem}.json")
        self._add(plan, target / f"{stem}.xsl", xsl, f"parameters_templates/{stem}.xsl")

        # zmienne wydzielone do variables/ + wpisy w rejestrze
        var_registry = self.variables_path / "_registry.json"
        for row in form.get('configVars', []):
            var_name = row.get('name', '').strip()
            if not var_name or not row.get('extract'):
                continue
            self._add(plan, self.variables_path / f"{var_name}.xsl",
                      self.normalize_variable_decls(row.get('xsl', '')),
                      f"variables/{var_name}.xsl")
            if row.get('scope') == 'global':
                meta = {"scope": "global"}
            else:
                order = row.get('order', '')
                meta = {"order": int(order) if str(order).strip().isdigit() else 10,
                        "uses": [u for u in row.get('uses', []) if u]}
            updated = self.registry_entry_text(var_registry, var_name, meta)
            if updated is not None:
                self._add(plan, var_registry, updated, "variables/_registry.json")

        # helpery + wpisy w rejestrze
        helper_registry = self.helpers_path / "_registry.json"
        for row in form.get('helpers', []):
            helper_name = row.get('name', '').strip()
            if not helper_name:
                continue
            self._add(plan, self.helpers_path / f"{helper_name}.xsl", row.get('xsl', ''),
                      f"helpers/{helper_name}.xsl")
            meta = {"uses": [u for u in row.get('uses', []) if u],
                    "globals": [g for g in row.get('globals', []) if g]}
            updated = self.registry_entry_text(helper_registry, helper_name, meta)
            if updated is not None:
                self._add(plan, helper_registry, updated, "helpers/_registry.json")

        return self._merge_registry_writes(plan)

    def _merge_registry_writes(self, plan: WritePlan) -> WritePlan:
        """Kilka zmiennych naraz oznacza kilka wpisów do tego samego rejestru — każdy
        policzony względem stanu z dysku. Scal je, licząc kolejne na wyniku poprzedniego."""
        merged: List[PlannedWrite] = []
        by_path: Dict[Path, PlannedWrite] = {}
        for write in plan.writes:
            if write.path.name != "_registry.json":
                merged.append(write)
                continue
            if write.path not in by_path:
                by_path[write.path] = write
                merged.append(write)
            else:
                by_path[write.path].content = write.content
        # rejestry aktualizujemy zawsze — to dopisek do istniejącego pliku, nie konflikt treści
        for write in by_path.values():
            if write.status == 'conflict':
                write.status = 'new'
                write.overwrite = True
        plan.writes = merged
        return plan

    # ------------------------------------------------------------------
    #  BACKUP I ZAPIS
    # ------------------------------------------------------------------

    def make_backup(self, writes: List[PlannedWrite],
                    stamp: Optional[str] = None) -> Optional[Path]:
        """Skopiuj nadpisywane pliki do _backup/RRRR-MM-DD_GG-MM-SS/, zachowując ścieżki."""
        existing = [w for w in writes if w.path.exists()]
        if not existing:
            return None
        stamp = stamp or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        target = self.backup_path / stamp
        for write in existing:
            rel = write.path.relative_to(self.base_path)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(write.path, dest)
        return target

    def apply(self, plan: WritePlan,
              stamp: Optional[str] = None) -> Tuple[List[Path], Optional[Path]]:
        """Kopia zapasowa, potem zapis. Zwraca (zapisane ścieżki, katalog kopii)."""
        writes = plan.to_apply()
        if not writes:
            return [], None
        backup = self.make_backup(writes, stamp)
        saved = []
        for write in writes:
            write.path.parent.mkdir(parents=True, exist_ok=True)
            write.path.write_text(write.content, encoding='utf-8')
            saved.append(write.path)
        return saved, backup

    # ------------------------------------------------------------------
    #  WALIDACJA
    # ------------------------------------------------------------------

    def run_validator(self) -> Tuple[int, str]:
        script = self.base_path / "validate_params.py"
        if not script.exists():
            return 1, f"Brak pliku {script}"

        # Wyjście podprocesu jest przekierowane, więc Python użyłby kodowania systemowego
        # (na Windows cp1250) i wywrócił się na '✅'/'⚠' z walidatora — UnicodeEncodeError
        # i kod wyjścia 1 mimo poprawnej bazy. Wymuszamy UTF-8 po obu stronach.
        env = dict(os.environ)
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        try:
            proc = subprocess.run(
                [sys.executable, str(script)], cwd=str(self.base_path),
                capture_output=True, text=True, encoding='utf-8', errors='replace',
                env=env, timeout=120)
        except (OSError, subprocess.SubprocessError) as exc:
            return 1, str(exc)
        return proc.returncode, (proc.stdout or '') + (proc.stderr or '')
