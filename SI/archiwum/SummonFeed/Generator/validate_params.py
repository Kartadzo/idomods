#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walidator spójności bazy parametrów summonFeed.

Sprawdza, czy pliki .json zgadzają się z .xsl oraz z rejestrami variables/ i helpers/.
Uruchom:  python validate_params.py
Kod wyjścia: 0 = brak błędów, 1 = są błędy (ostrzeżenia nie blokują).
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
PARAMS = BASE / "parameters_templates"
VARS = BASE / "variables"
HELPERS = BASE / "helpers"

VAR_REF = re.compile(r'\$([A-Za-z_À-ɏ][A-Za-z0-9_\-À-ɏ]*)')
VAR_DECL = re.compile(r'<xsl:variable\s+name\s*=\s*["\']([^"\']+)["\']')
CALL_TPL = re.compile(r'<xsl:call-template\s+name\s*=\s*["\']([^"\']+)["\']')
XSL_PARAM = re.compile(r'<xsl:param\s+name\s*=\s*["\']([^"\']+)["\']')
# musi odpowiadać wzorcowi z _apply_config_vars_to_xslt w summonFeed_generator.py
CONFIGVAR_DECL = r"<xsl:variable name=['\"]{name}['\"]>.*?</xsl:variable>"

errors, warnings = [], []


def err(param, msg):
    errors.append(f"  ✗ {param}: {msg}")


def warn(param, msg):
    warnings.append(f"  ⚠ {param}: {msg}")


def load_registry(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith('_')}


def helper_closure(names, registry):
    """Domknięcie zależności helperów wg 'uses'."""
    out = set()

    def add(h):
        if h in out:
            return
        out.add(h)
        for dep in registry.get(h, {}).get("uses", []):
            add(dep)

    for n in names:
        add(n)
    return out


def main():
    var_reg = load_registry(VARS / "_registry.json")
    helper_reg = load_registry(HELPERS / "_registry.json")
    globals_ = {n for n, m in var_reg.items() if m.get("scope") == "global"}

    # --- rejestr zmiennych: pliki + zależności + kolejność ---
    for name, meta in var_reg.items():
        if not (VARS / f"{name}.xsl").exists():
            errors.append(f"  ✗ variables/_registry.json: brak pliku {name}.xsl")
        for dep in meta.get("uses", []):
            if dep not in var_reg:
                errors.append(f"  ✗ variables/_registry.json: {name}.uses → nieznana zmienna '{dep}'")
            elif meta.get("order", 0) < var_reg[dep].get("order", 0):
                errors.append(
                    f"  ✗ variables/_registry.json: {name} (order={meta.get('order')}) "
                    f"używa {dep} (order={var_reg[dep].get('order')}) — zależność musi mieć order ≤")

    # --- rejestr helperów: pliki + zależności ---
    for name, meta in helper_reg.items():
        if not (HELPERS / f"{name}.xsl").exists():
            errors.append(f"  ✗ helpers/_registry.json: brak pliku {name}.xsl")
        for dep in meta.get("uses", []):
            if dep not in helper_reg:
                errors.append(f"  ✗ helpers/_registry.json: {name}.uses → nieznany helper '{dep}'")

    # --- parametry ---
    count = 0
    # exclusiveGroup: grupa → {parametr: (structure, exclusiveDefaultFor)}
    exclusive: dict = {}
    PARAMS_OUTPUT: dict = {}
    for jf in sorted(PARAMS.glob("*.json")):
        if jf.name.startswith('_'):
            continue
        count += 1
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"  ✗ {jf.name}: niepoprawny JSON — {e}")
            continue

        name = data.get("name", jf.stem)
        for field in ("name", "description", "structure", "context", "output"):
            if not data.get(field):
                err(name, f"brak wymaganego pola '{field}'")
        if not data.get("description_pl"):
            warn(name, "brak 'description_pl' (opis PL)")
        if data.get("name") != jf.stem:
            err(name, f"pole 'name' ({data.get('name')}) ≠ nazwa pliku ({jf.stem})")

        PARAMS_OUTPUT[name] = data.get("output")
        group = data.get("exclusiveGroup")
        default_for = data.get("exclusiveDefaultFor", [])
        if group:
            if not isinstance(default_for, list):
                err(name, "'exclusiveDefaultFor' musi być listą nazw struktur")
                default_for = []
            for s in default_for:
                if s not in data.get("structure", []):
                    err(name, f"'exclusiveDefaultFor' wskazuje strukturę '{s}', "
                              f"której nie ma w 'structure'")
            exclusive.setdefault(group, {})[name] = (data.get("structure", []), default_for)
        elif default_for:
            warn(name, "'exclusiveDefaultFor' bez 'exclusiveGroup' — pole jest ignorowane")

        xsl_file = jf.with_suffix(".xsl")
        if not xsl_file.exists():
            err(name, f"brak pliku {xsl_file.name}")
            continue
        xsl = xsl_file.read_text(encoding="utf-8")

        # output musi występować w .xsl
        out = data.get("output", "")
        if out and f'name="{out}"' not in xsl and f"<{out}>" not in xsl:
            err(name, f"element '{out}' z pola 'output' nie występuje w {xsl_file.name}")

        # helpery: zadeklarowane muszą istnieć; wołane muszą być pokryte domknięciem
        declared = data.get("helpers", [])
        for h in declared:
            if not (HELPERS / f"{h}.xsl").exists():
                err(name, f"helper '{h}' zadeklarowany, ale brak helpers/{h}.xsl")
            if h not in helper_reg:
                warn(name, f"helper '{h}' spoza helpers/_registry.json")
        covered = helper_closure([h for h in declared if h in helper_reg], helper_reg) | set(declared)
        for called in set(CALL_TPL.findall(xsl)):
            if called not in covered:
                err(name, f"woła helper '{called}', którego nie ma w 'helpers'")

        # createVars: albo z rejestru (parametr zmigrowany), albo deklarowane inline (legacy)
        create = data.get("createVars", [])
        inline_decls = set(VAR_DECL.findall(xsl))
        registry_cvs = [cv for cv in create if cv in var_reg]
        for cv in create:
            if cv in var_reg:
                if not (VARS / f"{cv}.xsl").exists():
                    err(name, f"createVar '{cv}' bez pliku variables/{cv}.xsl")
            elif cv not in inline_decls:
                err(name, f"createVar '{cv}' nie jest ani w variables/_registry.json, "
                          f"ani deklarowany inline w {xsl_file.name}")

        # tekst efektywny = .xsl parametru + pliki jego zmiennych z rejestru
        # (zmienna/configVar może być używana wewnątrz innej zmiennej, nie w emisji)
        effective = xsl
        for cv in registry_cvs:
            f = VARS / f"{cv}.xsl"
            if f.exists():
                effective += "\n" + f.read_text(encoding="utf-8")

        for cv in registry_cvs:
            if f"${cv}" not in effective:
                warn(name, f"createVar '{cv}' zadeklarowany, ale nieużywany")

        # configVars używane?
        cfg_names = [c["name"] for c in data.get("configVars", [])]
        for c in cfg_names:
            if f"${c}" not in effective:
                warn(name, f"configVar '{c}' zadeklarowany, ale nieużywany")

        # Czy generator dostarczy wartość configVara? Są trzy poprawne drogi:
        #   • parametr zmigrowany (wszystkie createVars w rejestrze) → deklaracja z preambuły,
        #   • configVar o nazwie zmiennej globalnej → deklaracja wstrzykiwana po <xsl:output>,
        #   • legacy → podmiana w .xsl wzorcem CONFIGVAR_DECL.
        # Deklaracja w innej formie (np. self-closing z select=) jest po cichu ignorowana
        # i parametr zawsze bierze wartość domyślną.
        migrated = bool(create) and all(cv in var_reg for cv in create)
        for c in cfg_names:
            declared_replaceable = re.search(
                CONFIGVAR_DECL.format(name=re.escape(c)), xsl, flags=re.DOTALL)
            if migrated or c in globals_:
                if declared_replaceable:
                    warn(name, f"configVar '{c}' zadeklarowany w {xsl_file.name}, choć wartość "
                               f"dostarcza preambuła/blok globalny — deklaracja jest zbędna")
            elif not declared_replaceable:
                err(name, f"configVar '{c}' nie ma w {xsl_file.name} deklaracji w formie "
                          f"<xsl:variable name=\"{c}\">…</xsl:variable> — generator jej nie "
                          f"podmieni i wartość z konfiguracji zostanie zignorowana")

        # referencje $zmienna: pokryte przez configVars / createVars / lokalne / globalne / params
        local = inline_decls | set(XSL_PARAM.findall(xsl))
        known = set(cfg_names) | set(create) | local | globals_
        for ref in sorted(set(VAR_REF.findall(xsl))):
            if ref not in known and ref not in var_reg:
                warn(name, f"referencja ${ref} bez deklaracji (configVar/createVar/global/lokalna)")

    # --- grupy wykluczające się: jeden domyślny na strukturę, spójne wyjście ---
    for group, members in exclusive.items():
        if len(members) < 2:
            warn(f"grupa '{group}'", "ma tylko jeden parametr — 'exclusiveGroup' nic nie wnosi")
        outs = {PARAMS_OUTPUT.get(m) for m in members}
        if len(outs) > 1:
            warn(f"grupa '{group}'", "parametry emitują różne elementy 'output' "
                                    f"({', '.join(sorted(str(o) for o in outs))}) — "
                                    f"czy na pewno się wykluczają?")
        structures = {s for structs, _ in members.values() for s in structs}
        for s in sorted(structures):
            in_struct = [m for m, (structs, _) in members.items() if s in structs]
            defaults = [m for m, (_, dflt) in members.items() if s in dflt]
            if len(defaults) > 1:
                errors.append(f"  ✗ grupa '{group}': dla struktury '{s}' kilka parametrów "
                              f"jest domyślnych ({', '.join(sorted(defaults))})")
            elif not defaults and len(in_struct) > 1:
                warnings.append(f"  ⚠ grupa '{group}': dla struktury '{s}' żaden z "
                                f"{len(in_struct)} parametrów nie ma 'exclusiveDefaultFor' "
                                f"— domyślnie zaznaczy się pierwszy alfabetycznie")

    print(f"Sprawdzono {count} parametrów, {len(var_reg)} zmiennych, {len(helper_reg)} helperów.\n")
    if errors:
        print(f"BŁĘDY ({len(errors)}):")
        print("\n".join(errors))
    if warnings:
        print(f"\nOSTRZEŻENIA ({len(warnings)}):")
        print("\n".join(warnings))
    if not errors and not warnings:
        print("✅ Wszystko spójne.")
    elif not errors:
        print("\n✅ Brak błędów (same ostrzeżenia).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
