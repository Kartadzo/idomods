#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import io
import requests
from lxml import etree

xml_url    = 'https://ara.waw.pl/wymiana/ara.xml?_gl=1*14loj5u*_ga*MjIwMDk5NDAuMTc1MjUwMTk4MQ..*_ga_2QRB642E1C*czE3NTI1MDE5ODAkbzEkZzEkdDE3NTI1MDIwNjUkajU5JGwwJGgxNzk4NjM0OTUw'
xslt_file  = 'synch_template.xml'
out_xml    = 'output.xml'
out_csv    = 'output.csv'
record_tag = 'item'

parser = etree.XMLParser(encoding='utf-8', recover=True)

try:
    resp     = requests.get(xml_url, timeout=10)
    resp.raise_for_status()
    xml_tree = etree.parse(io.BytesIO(resp.content), parser)
    print(f"Pobrano i sparsowano XML z: {xml_url}")
except Exception as e:
    print(f"Błąd pobierania/parowania XML z URL: {e}", file=sys.stderr)
    sys.exit(1)

try:
    xslt_tree = etree.parse(xslt_file, parser)
    print(f"Wczytano szablon XSLT: {xslt_file}")
except (OSError, etree.XMLSyntaxError) as e:
    print(f"Błąd wczytywania XSLT: {e}", file=sys.stderr)
    sys.exit(1)

transform   = etree.XSLT(xslt_tree)
result_tree = transform(xml_tree)

#Zapisz wynikowy XML
xml_bytes = etree.tostring(
    result_tree,
    pretty_print=True,
    xml_declaration=True,
    encoding='utf-8'
)
os.makedirs(os.path.dirname(out_xml) or '.', exist_ok=True)
with open(out_xml, 'wb') as f:
    f.write(xml_bytes)
print(f"Wynik XML zapisano w: {out_xml}")

#Parsujemy rekordy <record_tag> bez względu na namespace
root    = result_tree.getroot()
records = root.xpath(f'.//*[local-name()="{record_tag}"]')
print(f" Znaleziono {len(records)} elementów <{record_tag}>")

#Jeśli brak rekordów, twórz pusty CSV i zakończ
if not records:
    open(out_csv, 'w', encoding='utf-8').close()
    print(f"Nie znaleziono <{record_tag}>, utworzono pusty: {out_csv}")
    sys.exit(0)

#Nagłówki – nazwy bezpośrednich pod-elementów pierwszego <record_tag>
columns = []
seen    = set()
for child in records[0]:
    col = child.tag.split('}', 1)[-1]
    if col not in seen:
        seen.add(col)
        columns.append(col)

os.makedirs(os.path.dirname(out_csv) or '.', exist_ok=True)
with open(out_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(columns)
    for rec in records:
        row = []
        for col in columns:
            nodes = rec.xpath(f'./*[local-name()="{col}"]')
            el    = nodes[0] if nodes else None
            row.append((el.text or '').strip() if el is not None else '')
        writer.writerow(row)


print(f"Wynik CSV zapisano w: {out_csv}")
