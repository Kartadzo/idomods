#!/usr/bin/env python3
# python transform_xml/run.py

import os
import sys
import csv
from lxml import etree

# —————————————— ustaw ścieżki ——————————————
xml_file   = 'source.xml'
xslt_file  = 'test.xslt'
out_xml    = 'output.xml'
out_csv    = 'output.csv'

# —————————— parser UTF-8 z recover ——————————
parser = etree.XMLParser(encoding='utf-8', recover=True)
try:
    xml_tree  = etree.parse(xml_file,  parser)
    xslt_tree = etree.parse(xslt_file, parser)
except (OSError, etree.XMLSyntaxError) as e:
    print(f"❌ Błąd wczytywania XML/XSLT: {e}", file=sys.stderr)
    sys.exit(1)

# —————————— wykonaj XSLT ——————————
transform  = etree.XSLT(xslt_tree)
result_tree = transform(xml_tree)

# —————— zapisz wynikowy XML w UTF-8 ——————
xml_bytes = etree.tostring(
    result_tree,
    pretty_print=True,
    xml_declaration=True,
    encoding='utf-8'
)

# upewnij się, że katalog istnieje
xml_dir = os.path.dirname(out_xml)
if xml_dir and not os.path.isdir(xml_dir):
    os.makedirs(xml_dir, exist_ok=True)

with open(out_xml, 'wb') as f:
    f.write(xml_bytes)
print(f"✅ Wynik XML zapisano w: {out_xml}")

# —————— wygeneruj CSV z elementów <opinion> ——————
# parsujemy z bufora, by uniknąć wielokrotnego serializowania
root     = etree.fromstring(xml_bytes)
opinions = root.findall('.//opinion')

if not opinions:
    print("ℹ️  Nie znaleziono elementów <opinion> – CSV pozostaje pusty.")
    open(out_csv, 'w', encoding='utf-8').close()
    sys.exit(0)

# pobierz nazwy pól z pierwszej recenzji
headers = [child.tag for child in opinions[0]]

# upewnij się, że katalog istnieje
csv_dir = os.path.dirname(out_csv)
if csv_dir and not os.path.isdir(csv_dir):
    os.makedirs(csv_dir, exist_ok=True)

with open(out_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    for op in opinions:
        row = []
        for h in headers:
            el   = op.find(h)
            text = (el.text or '').strip() if el is not None else ''
            row.append(text)
        writer.writerow(row)

print(f"✅ Wynik CSV zapisano w: {out_csv}")
