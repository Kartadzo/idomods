#!/usr/bin/env python3
import csv
import sys
import os
import glob
import xml.etree.ElementTree as ET

def find_files():
    """
    Jeśli podano 3 argumenty: csv, xml, output.
    W przeciwnym razie auto-detekcja csv/xml i output = 'output.csv'.
    """
    if len(sys.argv) >= 4:
        return sys.argv[1], sys.argv[2], sys.argv[3]
    current = os.getcwd()
    csvs = glob.glob(os.path.join(current, '*.csv'))
    xmls = glob.glob(os.path.join(current, '*.xml'))
    if not csvs or not xmls:
        print("Brak pliku CSV lub XML w katalogu lub w argumencie.")
        sys.exit(1)
    print(f"Auto CSV: {csvs[0]}")
    print(f"Auto XML: {xmls[0]}")
    return csvs[0], xmls[0], 'output.csv'

def load_csv(csv_file):
    """Wczytuje wszystkie wiersze CSV do listy słowników."""
    with open(csv_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if 'ID' not in reader.fieldnames:
            print("CSV nie zawiera kolumny 'ID'.")
            sys.exit(1)
        return rows, reader.fieldnames

def load_xml_gtin_map(xml_file):
    """
    Parsuje XML i buduje mapę: { xml_id (bez sufiksu) : gtin }.
    Używa iterparse, by nie ładować całego pliku do pamięci.
    """
    mapping = {}
    ns = {'g': 'http://base.google.com/ns/1.0'}
    for evt, elem in ET.iterparse(xml_file, events=('end',)):
        tag = elem.tag
        # wykryj <item>
        if tag.endswith('item'):
            xml_id = None
            gtin = ''
            for child in elem:
                if child.tag.endswith('}id'):
                    text = child.text or ''
                    xml_id = text.strip().split('-', 1)[0]
                elif child.tag.endswith('}gtin'):
                    gtin = (child.text or '').strip()
            if xml_id:
                mapping[xml_id] = gtin
            elem.clear()
    return mapping

def write_output(rows, fieldnames, xml_map, out_file):
    """Zapisuje CSV z dodatkiem kolumny 'gtin'."""
    new_fields = fieldnames + ['gtin']
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        for row in rows:
            raw_id = row.get('ID', '').strip()
            key = raw_id.split('-', 1)[0] if raw_id else ''
            row['gtin'] = xml_map.get(key, '')
            writer.writerow(row)
    print(f"Zapisano plik wynikowy: {out_file}")

def main():
    csv_file, xml_file, out_file = find_files()
    print(f"CSV: {csv_file}")
    print(f"XML: {xml_file}")
    rows, fields = load_csv(csv_file)
    xml_map = load_xml_gtin_map(xml_file)
    write_output(rows, fields, xml_map, out_file)

if __name__ == '__main__':
    main()
