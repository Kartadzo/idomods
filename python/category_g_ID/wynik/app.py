#!/usr/bin/env python3
"""
generate_xslt_from_mapping.py
Wejście: CSV wygenerowany wcześniej (np. mapping_results.csv)
  oczekiwane kolumny (nazwa tolerancyjna): '@id' lub 'id', '/iai_category@id' lub 'iai', 'g:google_product_category' lub 'google'
Wyjście: mapping.xslt (XSLT 1.0) z <xsl:choose> gdzie każda gałąź <xsl:when>
 zawiera warunek porównujący zmienną $cat_id do zbioru id_kat_IAI i zwraca odpowiadające id_categori_Google
Przetwarzanie liniowe, niskie użycie pamięci.
"""
import argparse
import csv
import sys
import os
from collections import defaultdict

DEFAULT_INPUT = "mapping_results.csv"
DEFAULT_OUTPUT = "mapping.xslt"

# możliwe warianty nazw kolumn (tolerancyjne dopasowanie)
POSSIBLE_ID_COLS = ["@id", "id"]
POSSIBLE_IAI_COLS = ["/iai_category@id", "iai", "iai_id", "/iai_category@id"]
POSSIBLE_GOOGLE_COLS = ["g:google_product_category", "google", "google_product_category", "id_categori_Google"]

def detect_columns(fieldnames):
    fn = [f.strip() for f in (fieldnames or [])]
    id_col = next((c for c in POSSIBLE_ID_COLS if c in fn), None)
    iai_col = next((c for c in POSSIBLE_IAI_COLS if c in fn), None)
    google_col = next((c for c in POSSIBLE_GOOGLE_COLS if c in fn), None)
    return id_col, iai_col, google_col

def build_groups_from_csv(csv_path):
    groups = defaultdict(set)  # google_id -> set(iai_id)
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        id_col, iai_col, google_col = detect_columns(reader.fieldnames)
        if not iai_col or not google_col:
            raise SystemExit(f"Nie rozpoznano wymaganych kolumn w pliku CSV. Dostępne: {reader.fieldnames}")
        # iterujemy liniowo — pamięciooszczędnie
        for row in reader:
            google = (row.get(google_col) or "").strip()
            iai = (row.get(iai_col) or "").strip()
            if google and iai:
                groups[google].add(iai)
    return groups

def escape_xslt_literal(s):
    # prosty escape dla pojedynczego cudzysłowu w literałach '...'
    if "'" in s:
        # jeśli zawiera apostrof, użyj concat z częściami
        parts = s.split("'")
        # tworzymy concat('part0', "'", 'part1', ...)
        pieces = []
        for i, p in enumerate(parts):
            if p != "":
                pieces.append(f"'{p}'")
            if i < len(parts)-1:
                pieces.append('"\'"')  # literal single quote using double quotes
        return "concat(" + ", ".join(pieces) + ")"
    else:
        return f"'{s}'"

def generate_xslt(groups, output_path, variable_name="cat_id"):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">')
    lines.append('  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>')
    lines.append('  <xsl:template match="/">')
    lines.append(f'    <xsl:variable name="{variable_name}" select="category_idosell/@id"/>')
    lines.append('    <xsl:choose>')
    # sortujemy klucze dla przewidywalności
    for google_id in sorted(groups.keys(), key=lambda x: (x is None, x)):
        iai_set = groups[google_id]
        if not iai_set:
            continue
        # budujemy warunek łączony OR: $cat_id = 'iai1' or $cat_id = 'iai2' ...
        cond_parts = []
        for iai in sorted(iai_set):
            iai_escaped = iai.replace('"', '&quot;')
            cond_parts.append(f"${variable_name} = '{iai_escaped}'")
        condition = " or ".join(cond_parts)
        # wartość zwracana może zawierać apostrofy -> używamy escape_xslt_literal
        value_literal = escape_xslt_literal(google_id)
        lines.append(f'      <xsl:when test="{condition}">')
        lines.append(f'        <xsl:value-of select={value_literal} />')
        lines.append('      </xsl:when>')
    lines.append('      <xsl:otherwise>')
    lines.append('        <xsl:text>No match</xsl:text>')
    lines.append('      </xsl:otherwise>')
    lines.append('    </xsl:choose>')
    lines.append('  </xsl:template>')
    lines.append('</xsl:stylesheet>')
    # zapis
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("\n".join(lines))
    print(f"Zapisano XSLT do: {output_path}")

def parse_args():
    p = argparse.ArgumentParser(description="Generate XSLT from mapping CSV (mapping_results.csv).")
    p.add_argument("csv", nargs='?', default=DEFAULT_INPUT, help="Input CSV (mapping results).")
    p.add_argument("xslt", nargs='?', default=DEFAULT_OUTPUT, help="Output XSLT filename.")
    return p.parse_args()

def main():
    args = parse_args()
    csv_path = args.csv
    xslt_path = args.xslt
    if not os.path.isfile(csv_path):
        print(f"Plik CSV nie istnieje: {csv_path}", file=sys.stderr)
        sys.exit(1)
    groups = build_groups_from_csv(csv_path)
    if not groups:
        print("Brak grup do wygenerowania XSLT (plik CSV nie zawiera dopasowań).")
        sys.exit(0)
    generate_xslt(groups, xslt_path)

if __name__ == "__main__":
    main()
