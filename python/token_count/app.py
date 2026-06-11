#!/usr/bin/env python3
import csv
import sys
import os
import glob
from collections import Counter
import re

def find_csv_file():
    """
    Jeśli użytkownik poda nazwę pliku CSV jako argument, używamy jej;
    w przeciwnym wypadku przeszukujemy bieżący katalog.
    """
    if len(sys.argv) >= 2:
        csv_filename = sys.argv[1]
    else:
        current_dir = os.getcwd()
        csv_files = glob.glob(os.path.join(current_dir, "*.csv"))
        if not csv_files:
            print("Nie znaleziono plików CSV w bieżącym katalogu.")
            sys.exit(1)
        csv_filename = csv_files[0]
        print(f"Auto-detected CSV file: {csv_filename}")
    return csv_filename

def count_tokens(csv_filename, column_name, min_count=50):
    """
    Wczytuje plik CSV, tokenizuje zawartość wskazanej kolumny
    (z rozróżnieniem wielkości liter) i zlicza wystąpienia tokenów.
    """
    counter = Counter()
    try:
        with open(csv_filename, 'r', encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            if column_name not in reader.fieldnames:
                print(f"Plik CSV nie zawiera wymaganej kolumny '{column_name}'.")
                sys.exit(1)
            for row in reader:
                text = row.get(column_name, '')
                if text:
                    # Tokenizacja: rozdzielamy po znakach nieliterowych/cyfrowych
                    tokens = re.split(r'\W+', text)
                    tokens = [t for t in tokens if t]  # usuwamy puste
                    counter.update(tokens)
    except Exception as e:
        print("Błąd podczas odczytu pliku CSV:", e)
        sys.exit(1)
    # Filtrowanie po min_count
    filtered = {tok: cnt for tok, cnt in counter.items() if cnt >= min_count}
    return filtered

def write_output_csv(token_counts, output_filename):
    """
    Zapisuje tokeny i ich liczbę wystąpień do pliku CSV.
    """
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["token", "count"])
            for token, count in sorted(token_counts.items(), key=lambda x: (-x[1], x[0])):
                writer.writerow([token, count])
        print(f"Wynik zapisano w pliku: {output_filename}")
    except Exception as e:
        print("Błąd podczas zapisu pliku wynikowego:", e)
        sys.exit(1)

def main():
    csv_filename = find_csv_file()
    print("Odczyt pliku CSV:", csv_filename)
    token_counts = count_tokens(csv_filename, '/description/name[pol]', min_count=10)
    if not token_counts:
        print("Brak tokenów spełniających kryterium minimalnej liczby wystąpień.")
        sys.exit(0)
    output_filename = "token_counts.csv"
    write_output_csv(token_counts, output_filename)

if __name__ == '__main__':
    main()
