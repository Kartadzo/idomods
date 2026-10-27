import os
import csv
from collections import OrderedDict

def find_csv_files():
    return [f for f in os.listdir('.') if f.lower().endswith('.csv')]

def detect_id_column(fieldnames):
    """Wykrywa kolumnę ID — jeśli brak, używa pierwszej kolumny."""
    candidates = ["id", "ID", "Id", "sku", "SKU", "product_id", "g:id"]
    for c in candidates:
        if c in fieldnames:
            return c
    return fieldnames[0]  # fallback: pierwsza kolumna

def load_csv(path):
    """Wczytuje CSV do słownika {id: {kolumna: wartość}}"""
    data = OrderedDict()
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        id_column = detect_id_column(reader.fieldnames)

        for row in reader:
            idv = row.get(id_column, "").strip()
            if idv:
                data[idv] = row
    return data

def compare_rows(rowA, rowB):
    """Porównuje dwa rekordy CSV i zwraca listę różnic."""
    diffs = []
    all_keys = set(rowA.keys()) | set(rowB.keys())

    for key in all_keys:
        a = rowA.get(key, "").strip()
        b = rowB.get(key, "").strip()
        if a != b:
            diffs.append((key, a, b))

    return diffs

def generate_html_report(fileA, fileB, dataA, dataB, only_in_A, only_in_B, diffs_by_id):
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html><head><meta charset='utf-8'>")
    html.append("<title>Porównanie CSV</title>")
    html.append("""
    <style>
body {
    font-family: Arial, sans-serif;
    font-size: 14px;
    margin: 20px;
}

/* Cała tabela nie będzie rozciągać się na 100% */
table {
    border-collapse: collapse;
    width: 900px;          /* stała szerokość */
    max-width: 100%;       /* responsywność */
    margin-bottom: 20px;
    margin-left: auto;
    margin-right: auto;    /* centrowanie */
}

/* Kolumny mają stałą szerokość */
th, td {
    border: 1px solid #ccc;
    padding: 6px 10px;
    text-align: left;
    width: 200px;          /* kluczowa zmiana */
    word-break: break-word;
}

/* Nagłówki */
th {
    background: #f2f2f2;
    font-weight: bold;
}

/* Naprzemienne wiersze dla czytelności */
tr:nth-child(even) {
    background: #fafafa;
}

/* Wiersze z różnicami */
.diff {
    background: #ffe6e6 !important;
}

/* Brakujące ID */
.missing {
    background: #fff3cd !important;
}

/* Sekcje ID mają odstęp */
h3 {
    margin-top: 30px;
    margin-bottom: 10px;
    text-align: center;
}
</style>
    """)
    html.append("</head><body>")

    html.append("<h1>Porównanie dwóch plików CSV</h1>")
    html.append(f"<p><strong>Plik A:</strong> {fileA}<br><strong>Plik B:</strong> {fileB}</p>")

    html.append("<h2>Podsumowanie</h2>")
    html.append("<ul>")
    html.append(f"<li>Liczba rekordów w pliku A: {len(dataA)}</li>")
    html.append(f"<li>Liczba rekordów w pliku B: {len(dataB)}</li>")
    html.append(f"<li>ID tylko w pliku A: {len(only_in_A)}</li>")
    html.append(f"<li>ID tylko w pliku B: {len(only_in_B)}</li>")
    html.append(f"<li>Rekordy z różnicami: {len(diffs_by_id)}</li>")
    html.append("</ul>")

    html.append("<h2>Brakujące ID</h2>")
    html.append("<table><tr><th>ID</th><th>Status</th></tr>")
    for idv in only_in_A:
        html.append(f"<tr class='missing'><td>{idv}</td><td>Brak w pliku B</td></tr>")
    for idv in only_in_B:
        html.append(f"<tr class='missing'><td>{idv}</td><td>Brak w pliku A</td></tr>")
    html.append("</table>")

    html.append("<h2>Różnice w rekordach</h2>")
    if not diffs_by_id:
        html.append("<p><strong>Brak jakichkolwiek różnic.</strong></p>")
    else:
        for idv, diffs in diffs_by_id.items():
            html.append(f"<h3>ID: {idv}</h3>")
            html.append("<table>")
            html.append("<tr><th>Kolumna</th><th>Plik A</th><th>Plik B</th></tr>")
            for key, a, b in diffs:
                html.append(f"<tr class='diff'><td>{key}</td><td>{a}</td><td>{b}</td></tr>")
            html.append("</table>")

    html.append("</body></html>")

    with open("report.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html))

def main():
    print("=== Porównywanie dwóch plików CSV ===")

    csv_files = find_csv_files()
    if len(csv_files) != 2:
        print("W folderze muszą znajdować się dokładnie 2 pliki CSV.")
        print("Znaleziono:", csv_files)
        return

    fileA, fileB = csv_files
    print(f"Plik A: {fileA}")
    print(f"Plik B: {fileB}")

    dataA = load_csv(fileA)
    dataB = load_csv(fileB)

    idsA = set(dataA.keys())
    idsB = set(dataB.keys())

    only_in_A = sorted(idsA - idsB)
    only_in_B = sorted(idsB - idsA)
    common_ids = sorted(idsA & idsB)

    diffs_by_id = {}
    for idv in common_ids:
        diffs = compare_rows(dataA[idv], dataB[idv])
        if diffs:
            diffs_by_id[idv] = diffs

    with open("differences.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Kolumna", "W pliku A", "W pliku B"])

        for idv in only_in_A:
            writer.writerow([idv, "Brak w pliku B", "", ""])
        for idv in only_in_B:
            writer.writerow([idv, "Brak w pliku A", "", ""])

        for idv, diffs in diffs_by_id.items():
            for key, a, b in diffs:
                writer.writerow([idv, key, a, b])

    generate_html_report(fileA, fileB, dataA, dataB, only_in_A, only_in_B, diffs_by_id)

    print("\n=== Wynik zapisany w differences.csv oraz report.html ===")
    print(f"Brak w {fileB}: {len(only_in_A)}")
    print(f"Brak w {fileA}: {len(only_in_B)}")
    print(f"Rekordy z różnicami: {len(diffs_by_id)}")

if __name__ == "__main__":
    main()
