import csv
import xml.etree.ElementTree as ET

INPUT_FILE = "output.xml"
OUTPUT_FILE = "output.csv"

def extract_columns(item):
    """Zwraca listę kolumn z <p> wewnątrz <item>."""
    cols = []
    for p in item.findall(".//p"):
        text = (p.text or "").strip()
        if text:
            cols.append(text)
    return cols

def main():
    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()

    rows = []

    # pobierz wszystkie <item>
    for item in root.findall(".//item"):
        cols = extract_columns(item)
        if cols:
            rows.append(tuple(cols))  # tuple → łatwe usuwanie duplikatów

    # usuń duplikaty
    unique_rows = sorted(set(rows), key=lambda r: [c.lower() for c in r])

    # znajdź maksymalną liczbę kolumn
    max_cols = max(len(r) for r in unique_rows)

    # zapisz CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # nagłówki: col1, col2, col3...
        writer.writerow([f"col{i+1}" for i in range(max_cols)])
        for row in unique_rows:
            # uzupełnij brakujące kolumny pustymi polami
            padded = list(row) + [""] * (max_cols - len(row))
            writer.writerow(padded)

    print(f"Zapisano {len(unique_rows)} unikalnych wierszy do {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
