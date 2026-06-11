import csv
import os
from csv import DictWriter

# Funkcja ładująca dane z pliku CSV (delimiter: ;)
def load_csv(file_path, source, clients, clientSources):
    with open(file_path, mode='r', encoding='utf-8-sig', newline='') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        for row in reader:
            add_record(row, source, clients, clientSources)

def add_record(record, source, clients, clientSources):
    # Używamy pola "email" jako klucza (możesz zmienić klucz, np. "client_id")
    key = record.get("email", "").strip().lower()
    if not key:
        return  # pomijamy rekordy bez e-maila
    if key not in clients:
        clients[key] = record
        clientSources[key] = {source}
    else:
        clientSources[key].add(source)
        # Jeśli rekord pochodzi z wyższego źródła (mniejszy priorytet), zastępujemy
        best_source = min(clientSources[key], key=lambda s: PRIORITY[s])
        if PRIORITY[source] < PRIORITY[best_source]:
            clients[key] = record

def write_csv(file_path, records, fieldnames):
    with open(file_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = DictWriter(outfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        writer.writerows(records)

def transform_record_with_mailing(record):
    # Pobranie oryginalnej wartości z kolumny mailing
    mailing_val = record.get("mailing", "").strip()
    # Jeśli komórka zawiera 'n' (bez względu na wielkość liter) ustawiamy "0"
    # Jeśli zawiera dowolną cyfrę, ustawiamy "1"
    if mailing_val.lower() == "n":
        result_mailing = "0"
    elif any(ch.isdigit() for ch in mailing_val):
        result_mailing = "1"
    else:
        result_mailing = "0"
    
    return {
        "First Name": record.get("firstname", "").strip(),
        "Last Name": record.get("lastname", "").strip(),
        "City": record.get("city", "").strip(),
        "Country": record.get("country", "").strip(),
        "Phone": record.get("phone", "").strip(),
        "Email": record.get("email", "").strip(),
        "Mailing": result_mailing,
    }

def process_files():
    # Wyszukujemy pliki csv, które nie zaczynają się od "output"
    all_files = [f for f in os.listdir(".") if f.endswith(".csv") and not f.startswith("output")]
    # Uporządkujemy pliki alfabetycznie – przyjmujemy, że pierwsze trzy wyznaczają priorytet
    input_files = sorted(all_files)[:3]
    if len(input_files) < 1:
        raise Exception("Nie znaleziono żadnych plików wejściowych CSV.")
    
    # Ustalmy priorytet: pierwszy plik → najwyższy priorytet, następny → średni, trzeci → najniższy
    global PRIORITY
    PRIORITY = { input_files[0]: 1 }
    if len(input_files) > 1:
        PRIORITY[input_files[1]] = 2
    if len(input_files) > 2:
        PRIORITY[input_files[2]] = 3

    print("Pliki wejściowe:", input_files)
    
    # Słowniki do grupowania rekordów
    clients = {}
    clientSources = {}
    
    # Wczytujemy dane z każdego pliku
    for file in input_files:
        load_csv(file, file, clients, clientSources)
    
    # Grupujemy rekordy według ostatecznego źródła
    grouped = {"file1": [], "file2": [], "file3": []}
    # Mapujemy źródło na klucz, w zależności od numeru w kolejności
    sourceMapping = {}
    if input_files:
        sourceMapping[input_files[0]] = "file1"
    if len(input_files) > 1:
        sourceMapping[input_files[1]] = "file2"
    if len(input_files) > 2:
        sourceMapping[input_files[2]] = "file3"
    
    for key, record in clients.items():
        best_source = min(clientSources[key], key=lambda s: PRIORITY[s])
        mapped = sourceMapping.get(best_source)
        if mapped:
            grouped[mapped].append(record)
    
    # Nagłówki wyjściowe, dodajemy kolumnę mailing
    desired_fieldnames = ["First Name", "Last Name", "City", "Country", "Phone", "Email", "Mailing"]
    
    # Transformacja rekordów do wyjściowej struktury
    output1 = [transform_record_with_mailing(rec) for rec in grouped["file1"]]
    output2 = [transform_record_with_mailing(rec) for rec in grouped["file2"]]
    output3 = [transform_record_with_mailing(rec) for rec in grouped["file3"]]
    
    # Zapis do plików wyjściowych: nazwa pliku = "output_" + oryginalna nazwa wejściowego pliku
    if input_files:
        write_csv("output_" + input_files[0], output1, desired_fieldnames)
    if len(input_files) > 1:
        write_csv("output_" + input_files[1], output2, desired_fieldnames)
    if len(input_files) > 2:
        write_csv("output_" + input_files[2], output3, desired_fieldnames)
    
    print("Przetwarzanie zakończone.")

if __name__ == "__main__":
    process_files()
