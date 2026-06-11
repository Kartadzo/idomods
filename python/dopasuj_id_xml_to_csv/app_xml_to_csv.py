import csv
from lxml import etree

# Pliki wejściowe
xml_file = 'ProductsBackupShop00001.xml'  # Duży plik XML (5 GB)
csv_file = 'lista_id_do_nazw.csv'         # Plik CSV z ID do zachowania

# Wczytaj ID z pliku CSV do zbioru
ids_to_keep = set()
with open(csv_file, mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    next(reader)  # Pomijamy nagłówek
    for row in reader:
        ids_to_keep.add(row[0])

# Definiujemy nagłówki dla pliku wynikowego CSV
header = ["id", "name"]

# Definiujemy przestrzeń nazw dla atrybutu xml:lang
namespaces = {'xml': 'http://www.w3.org/XML/1998/namespace'}

# Otwieramy plik wynikowy CSV
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)

    # Używamy iterparse do efektywnego przetwarzania dużego pliku XML
    context = etree.iterparse(xml_file, events=('end',), tag='product')

    for event, product in context:
        product_id = product.get('id')
        if product_id in ids_to_keep:
            # Pobieramy nazwę z 'description/name[@xml:lang="pol"]'
            name = ''
            description = product.find('description')
            if description is not None:
                # Szukamy elementu <name xml:lang="pol">
                name_element = description.find('name[@xml:lang="pol"]', namespaces)
                if name_element is not None and name_element.text:
                    name = name_element.text.strip()
            # Zapisujemy wiersz do pliku CSV tylko, jeśli nazwa została znaleziona
            if name:
                writer.writerow([product_id, name])
        # Czyścimy element z pamięci, aby zaoszczędzić miejsce
        product.clear()
        while product.getprevious() is not None:
            del product.getparent()[0]
