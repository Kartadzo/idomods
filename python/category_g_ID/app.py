#!/usr/bin/env python3
"""
map_xml_to_csv.py
- Tworzy mapowanie między '@id' z CSV a '/iai_category@id'
- Parsuje XML RSS/Google Merchant feed (streaming) i dla każdego <item>
  pobiera g:id (bez sufiksu po '-') oraz g:google_product_category
- Jeżeli g:id występuje w mapowaniu CSV, zapisuje linię do output CSV:
  @id, /iai_category@id, g:google_product_category

Zaprojektowany do pracy z dużymi plikami (streaming, opcjonalnie sqlite jako magazyn map)
"""
import argparse
import csv
import os
import sys
import glob
import sqlite3
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Iterable

DEFAULT_OUTPUT = "mapping_results.csv"

def find_files(args):
    if args.csv and args.xml:
        return args.csv, args.xml
    # automatyczne wykrywanie
    cur = os.getcwd()
    csv_files = glob.glob(os.path.join(cur, "*.csv"))
    xml_files = glob.glob(os.path.join(cur, "*.xml"))
    if not csv_files or not xml_files:
        print("Nie znaleziono plików CSV lub XML w bieżącym katalogu. Podaj jako argumenty.", file=sys.stderr)
        sys.exit(1)
    print(f"Auto-detected CSV file: {csv_files[0]}")
    print(f"Auto-detected XML file: {xml_files[0]}")
    return csv_files[0], xml_files[0]

def build_csv_mapping_in_memory(csv_filename: str, id_field='@id', iai_field='/iai_category@id') -> Dict[str,str]:
    mapping = {}
    with open(csv_filename, 'r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or []
        if id_field not in fields or iai_field not in fields:
            raise ValueError(f"Plik CSV musi zawierać kolumny {id_field} i {iai_field}. Aktualne: {fields}")
        for row in reader:
            key = (row.get(id_field) or "").strip()
            val = (row.get(iai_field) or "").strip()
            if key:
                mapping[key] = val
    return mapping

def build_csv_mapping_sqlite(csv_filename: str, sqlite_db: str, id_field='@id', iai_field='/iai_category@id'):
    # Tworzy sqlite DB z tabelą mapping(id TEXT PRIMARY KEY, iai TEXT)
    conn = sqlite3.connect(sqlite_db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS mapping")
    cur.execute("CREATE TABLE mapping(id TEXT PRIMARY KEY, iai TEXT)")
    conn.commit()
    with open(csv_filename, 'r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or []
        if id_field not in fields or iai_field not in fields:
            conn.close()
            raise ValueError(f"Plik CSV musi zawierać kolumny {id_field} i {iai_field}. Aktualne: {fields}")
        to_insert = []
        batch = 0
        for row in reader:
            key = (row.get(id_field) or "").strip()
            val = (row.get(iai_field) or "").strip()
            if key:
                to_insert.append((key, val))
            if len(to_insert) >= 10000:
                cur.executemany("INSERT OR REPLACE INTO mapping(id, iai) VALUES (?,?)", to_insert)
                conn.commit()
                batch += 1
                print(f"Inserted batch {batch*10000} rows into sqlite...", end='\r')
                to_insert = []
        if to_insert:
            cur.executemany("INSERT OR REPLACE INTO mapping(id, iai) VALUES (?,?)", to_insert)
            conn.commit()
    print("\nFinished building sqlite mapping.")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_id ON mapping(id)")
    conn.commit()
    return conn

def iter_xml_items(xml_filename: str) -> Iterable[ET.Element]:
    """
    Yield each <item> element (Element) using iterparse in streaming mode.
    Obsługuje namespace'y przez porównanie końcówki tagu (localname).
    """
    # Używamy iterparse z event 'end' i clear() po przetworzeniu elementu
    for event, elem in ET.iterparse(xml_filename, events=("end",)):
        tag = elem.tag
        # obsługa namespace: lokalna nazwa to wszystko po '}' jeśli obecne
        local = tag.split('}', 1)[-1] if '}' in tag else tag
        if local == 'item':
            yield elem
            elem.clear()

def localname(tag: str) -> str:
    return tag.split('}', 1)[-1] if '}' in tag else tag

def extract_from_item(item: ET.Element):
    """
    Zwraca (xml_id_without_suffix, google_product_category_or_None)
    Szuka elementów g:id oraz g:google_product_category (mogą mieć namespace)
    """
    xml_id = None
    google_cat = None
    for child in item:
        ln = localname(child.tag)
        if ln == 'id':
            if child.text:
                xml_id = child.text.strip()
                if '-' in xml_id:
                    xml_id = xml_id.split('-', 1)[0]
        elif ln == 'google_product_category':
            if child.text:
                google_cat = child.text.strip()
    return xml_id, google_cat

def process_streaming(xml_filename: str, csv_mapping_in_mem: Optional[Dict[str,str]],
                      sqlite_conn: Optional[sqlite3.Connection], output_filename: str):
    out_fh = open(output_filename, 'w', newline='', encoding='utf-8')
    writer = csv.writer(out_fh)
    writer.writerow(['@id', '/iai_category@id', 'g:google_product_category'])
    matched = 0
    processed = 0
    cur = sqlite_conn.cursor() if sqlite_conn else None

    for item in iter_xml_items(xml_filename):
        processed += 1
        xml_id, google_cat = extract_from_item(item)
        if not xml_id or not google_cat:
            continue
        iai = None
        if csv_mapping_in_mem is not None:
            iai = csv_mapping_in_mem.get(xml_id)
        else:
            # sqlite lookup
            cur.execute("SELECT iai FROM mapping WHERE id = ?", (xml_id,))
            row = cur.fetchone()
            iai = row[0] if row else None
        if iai:
            writer.writerow([xml_id, iai, google_cat])
            matched += 1
        if processed % 10000 == 0:
            print(f"Processed {processed} items, matched {matched}", end='\r')
    out_fh.close()
    print(f"\nDone. Processed {processed} items, matched {matched}. Output: {output_filename}")

def parse_args():
    p = argparse.ArgumentParser(description="Map XML g:id -> CSV /iai_category@id and output csv results.")
    p.add_argument("csv", nargs='?', help="Input CSV file (contains @id and /iai_category@id)")
    p.add_argument("xml", nargs='?', help="Input XML file (Google Merchant / RSS)")
    p.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="Output CSV file")
    p.add_argument("--use-db", action="store_true", help="Use sqlite DB for CSV mapping (memory safe for huge CSVs)")
    p.add_argument("--db-file", default="mapping.db", help="SQLite DB filename (when --use-db)")
    p.add_argument("--id-field", default='@id', help="CSV column name used as key")
    p.add_argument("--iai-field", default='/iai_category@id', help="CSV column name with iai id")
    return p.parse_args()

def main():
    args = parse_args()
    csv_filename, xml_filename = find_files(args)
    print("CSV:", csv_filename)
    print("XML:", xml_filename)
    if args.use_db:
        print("Building sqlite mapping (streaming CSV)...")
        conn = build_csv_mapping_sqlite(csv_filename, args.db_file, id_field=args.id_field, iai_field=args.iai_field)
        csv_map = None
    else:
        print("Loading CSV mapping into memory (may use more RAM)...")
        csv_map = build_csv_mapping_in_memory(csv_filename, id_field=args.id_field, iai_field=args.iai_field)
        conn = None

    process_streaming(xml_filename, csv_map, conn, args.output)

    if conn:
        conn.close()

if __name__ == "__main__":
    main()
