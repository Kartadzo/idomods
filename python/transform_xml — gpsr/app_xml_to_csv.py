import csv
import xml.etree.ElementTree as ET

INPUT_FILE = "output.xml"
OUTPUT_FILE = "output.csv"

# 🔧 KONFIGURACJA SEPARATORA CSV
CSV_SEPARATOR = ";"   # np. ",", ";", "|", "\t"

def extract_columns(item):
    """
    Zwraca dict: {tag: value} dla każdego pola w <item>.
    """
    row = {}
    for child in item:
        tag = child.tag.strip()
        value = (child.text or "").strip()
        row[tag] = value
    return row

def main():
    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()

    rows = []

    # pobierz wszystkie <item>
    items = root.findall(".//item")
    if not items:
        print("Brak elementów <item> w XML.")
        return

    # pierwszy item → ustala kolejność kolumn
    first_row = extract_columns(items[0])
    column_order = list(first_row.keys())

    # przetwarzanie wszystkich itemów
    for item in items:
        row = extract_columns(item)
        rows.append(row)

    # usuń duplikaty (dict → tuple → set)
    unique_rows = {tuple(sorted(r.items())) for r in rows}

    # konwersja z powrotem do dict
    unique_dicts = [dict(t) for t in unique_rows]

    # zapisz CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=CSV_SEPARATOR)

        # nagłówki w kolejności z pierwszego itemu
        writer.writerow(column_order)

        for row in unique_dicts:
            writer.writerow([row.get(col, "") for col in column_order])

    print(f"Zapisano {len(unique_dicts)} unikalnych wierszy do {OUTPUT_FILE} (separator: '{CSV_SEPARATOR}')")

if __name__ == "__main__":
    main()
