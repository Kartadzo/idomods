#!/usr/bin/env python3
import csv
import sys
import os
import glob

def find_csv_file():
    """
    Jeśli nazwa pliku CSV jest podana jako argument, używamy jej;
    w przeciwnym wypadku wyszukujemy pierwszy plik CSV w bieżącym katalogu.
    """
    if len(sys.argv) >= 2:
        return sys.argv[1]
    else:
        csv_files = glob.glob("*.csv")
        if not csv_files:
            print("Nie znaleziono plików CSV w bieżącym katalogu.")
            sys.exit(1)
        print(f"Auto-detected CSV file: {csv_files[0]}")
        return csv_files[0]

def extract_value(text, prefix):
    """
    Z podanego wieloliniowego tekstu wyodrębnia wartość z linii, która zaczyna się od podanego prefixu.
    Jeśli taka linia występuje, zwraca część po separatorze backslash.
    """
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            parts = line.split("\\", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return ""

def row_has_group(text):
    """
    Sprawdza, czy w wieloliniowym tekście znajduje się linia zaczynająca się od "GroupID\\".
    """
    for line in text.splitlines():
        if line.strip().startswith("GroupID\\"):
            return True
    return False

def remove_existing_group_marker(text):
    """
    Usuwa linie zaczynające się od "GroupID\\" z wieloliniowego tekstu.
    """
    lines = text.splitlines()
    filtered = [line for line in lines if not line.strip().startswith("GroupID\\")]
    return "\n".join(filtered)

def append_line_to_cell(cell_value, line_to_append):
    """
    Dopisuje do zawartości komórki (jeśli nie jest pusta, dodaje znak nowej linii)
    i zwraca nowy ciąg.
    """
    if cell_value.strip():
        return cell_value.rstrip() + "\n" + line_to_append
    else:
        return line_to_append

def process_csv(input_filename, output_filename):
    """
    Przetwarza plik CSV.

    Dla każdego wiersza:
      - Aktualizuje kolumnę "/parameters/parameter@group_distinction":
            dzieli zawartość komórki "/parameters/parameter@textid[pol]" na linie.
            Linie zaczynające się od "Kolor podstawy\\" lub "Typ podstawy\\" zastępuje wartością "y",
            pozostałe – "n". Na końcu dodatkowo dopisuje linię "n".
      - Do kolumn "/parameters/parameter@distinction" oraz "/parameters/parameter@projector_hide"
            dołącza linię "y".
      - Grupowanie:
            Jeśli w komórce "/parameters/parameter@textid[pol]" nie ma jeszcze markera grupowego,
            ustalany jest klucz grupujący _dla wartości GroupID_ jako krotka:
                 (materiał, kolor)
            gdzie:
                 materiał = extract_value( tekst, "Materiał fotela\\" )  (domyślnie "Unknown")
                 kolor    = extract_value( tekst, "Kolor fotela\\" )         (domyślnie "Unknown")
            Pierwszy rekord (jego wartość z kolumny "@id") staje się reprezentantem tej grupy.
            Marker grupowy ("GroupID\<reprezentant>") dołączany jest do komórki "/parameters/parameter@textid[pol]"
            oraz w kolumnie "/group@id" zapisujemy tę wartość.
            Natomiast kolumny grupowe ("/group/group_by_parameter@name[pol]" oraz
            "/group/group_by_parameter/product_value@name[pol]") pozostają zgodnie z wcześniejszą logiką,
            czyli:
                 • "/group/group_by_parameter@name[pol]" ustawione jest na stały tekst "Kolor podstawy \\ Typ podstawy",
                 • "/group/group_by_parameter/product_value@name[pol]" zawiera konkatenację wartości: 
                       extract_value(text, "Kolor podstawy\\")  \\  extract_value(text, "Typ podstawy\\")
      
    W pliku wynikowym zapisywane są jedynie następujące kolumny:
         @id,
         /parameters/parameter@textid[pol],
         /parameters/parameter@distinction,
         /parameters/parameter@group_distinction,
         /parameters/parameter@projector_hide,
         /group@id,
         /group/group_by_parameter@name[pol],
         /group/group_by_parameter/product_value@name[pol]
    """
    out_fieldnames = [
        "@id",
        "/parameters/parameter@textid[pol]",
        "/parameters/parameter@distinction",
        "/parameters/parameter@group_distinction",
        "/parameters/parameter@projector_hide",
        "/group@id",
        "/group/group_by_parameter@name[pol]",
        "/group/group_by_parameter/product_value@name[pol]"
    ]

    # Mapowanie grup: klucz = (materiał, kolor) -> reprezentant grupy (pierwsze @id)
    group_mapping = {}

    with open(input_filename, "r", encoding="utf-8-sig", newline="") as infile, \
         open(output_filename, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile, delimiter=",")
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames, delimiter=",")
        writer.writeheader()

        for row in reader:
            text_field = row.get("/parameters/parameter@textid[pol]", "")

            # Aktualizacja kolumny "/parameters/parameter@group_distinction":
            group_dist_lines = []
            for line in text_field.splitlines():
                stripped = line.strip()
                if stripped.startswith("Kolor podstawy\\") or stripped.startswith("Typ podstawy\\"):
                    group_dist_lines.append("y")
                else:
                    group_dist_lines.append("n")
            new_group_dist = "\n".join(group_dist_lines)
            new_group_dist = append_line_to_cell(new_group_dist, "n")
            row["/parameters/parameter@group_distinction"] = new_group_dist

            # Dopisujemy linię "y" do kolumn "/parameters/parameter@distinction" oraz "/parameters/parameter@projector_hide"
            row["/parameters/parameter@distinction"] = append_line_to_cell(row.get("/parameters/parameter@distinction", ""), "y")
            row["/parameters/parameter@projector_hide"] = append_line_to_cell(row.get("/parameters/parameter@projector_hide", ""), "y")

            # Grupowanie – jeśli w tekście nie ma jeszcze markera grupowego
            if not row_has_group(text_field):
                # Wyznaczamy klucz grupujący _dla pól GroupID_ przy użyciu dwóch reguł:
                material = extract_value(text_field, "Materiał fotela\\")
                kolor = extract_value(text_field, "Kolor fotela\\")
                if not material:
                    material = "Unknown"
                if not kolor:
                    kolor = "Unknown"
                group_key = (material, kolor)
                if group_key not in group_mapping:
                    group_mapping[group_key] = row.get("@id", "").strip()
                group_rep_id = group_mapping[group_key]
                group_marker = f"GroupID\\{group_rep_id}"
                new_text_field = remove_existing_group_marker(text_field).rstrip()
                new_text_field = append_line_to_cell(new_text_field, group_marker)
                row["/parameters/parameter@textid[pol]"] = new_text_field

                # Uzupełniamy kolumnę "/group@id" – _tylko ta wartość_ opiera się na nowym (dwukrotnym) grupowaniu
                row["/group@id"] = group_rep_id

                # Pozostałe kolumny grupowe pozostają według starej logiki:
                row["/group/group_by_parameter@name[pol]"] = "Kolor podstawy \\ Typ podstawy"
                kolor_podstawy = extract_value(text_field, "Kolor podstawy\\")
                typ_podstawy = extract_value(text_field, "Typ podstawy\\")
                row["/group/group_by_parameter/product_value@name[pol]"] = f"{kolor_podstawy} \\ {typ_podstawy}".strip()
            # Jeśli wiersz już posiada marker, zakładamy, że kolumny grupowe są już uzupełnione.

            new_row = { key: row.get(key, "") for key in out_fieldnames }
            writer.writerow(new_row)

    print("Utworzono grupy (klucz: (Materiał fotela, Kolor fotela)):")
    for key, rep in group_mapping.items():
        print(f"  Grupa dla {key}: GroupID\\{rep}")
    print(f"Wynik zapisano w pliku: {output_filename}")

def main():
    input_file = find_csv_file()
    output_file = "output_grouped.csv"
    process_csv(input_file, output_file)

if __name__ == "__main__":
    main()
