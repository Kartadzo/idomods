import os
import shutil
import sys
from lxml import etree
from tqdm import tqdm

INPUT = "source.xml"
XSLT_FILE = "feediai_ceny_omnibus_for_xml.xslt"
CHUNK_DIR = "chunks"
RESULT_DIR = "results"
FINAL_OUTPUT = "output.xml"

CHUNK_SIZE = 12000
ELEMENT_NAME = "product"

os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

def find_input_file():
    if os.path.exists(INPUT):
        return INPUT

    print("Nie znaleziono source.xml — szukam plików XML w folderze...")

    xml_files = [
        f for f in os.listdir(".")
        if f.lower().endswith(".xml") and os.path.isfile(f)
    ]

    if not xml_files:
        raise FileNotFoundError("Brak plików XML w folderze.")

    largest = max(xml_files, key=lambda f: os.path.getsize(f))
    return largest


def confirm_file(path):
    print(f"\nPlik do przetwarzania: {path}")
    answer = input("Czy użyć proponowanego pliku? (tak/yes/t/y): ").strip().lower()

    if answer in ("tak", "t", "yes", "y"):
        return True

    raise Exception("Przerwano działanie skryptu. Nazwij plik poprawnie lub wyczyść folder z innych plików XML")
    print("Bye")
    return False

def chunk_xml(input_file):
    print("\n[1/4] Wczytywanie pliku XML i przygotowywanie chunków...")

    context = etree.iterparse(input_file, events=("end",), tag=ELEMENT_NAME)

    chunk_index = 1
    count = 0
    buffer = []

    for event, elem in tqdm(context, desc="Tworzenie chunków", unit="elem"):
        buffer.append(etree.tostring(elem, encoding="utf-8"))
        count += 1

        if count % CHUNK_SIZE == 0:
            save_chunk(buffer, chunk_index)
            buffer = []
            chunk_index += 1

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    if buffer:
        save_chunk(buffer, chunk_index)

def save_chunk(buffer, index):
    filename = os.path.join(CHUNK_DIR, f"chunk_{index:05d}.xml")
    with open(filename, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(b'<offer>\n<products>\n')
        for item in buffer:
            f.write(item)
            f.write(b"\n")
        f.write(b'</products>\n</offer>')

def transform_chunks():
    print("\n[2/4] Przetwarzanie XML...")

    xslt = etree.parse(XSLT_FILE)
    transform = etree.XSLT(xslt)

    files = sorted([f for f in os.listdir(CHUNK_DIR) if f.endswith(".xml")])

    for file in tqdm(files, desc="Przetwarzanie chunków", unit="chunk"):
        chunk_path = os.path.join(CHUNK_DIR, file)

        with open(chunk_path, "rb") as f:
            xml = etree.fromstring(f.read())

        result = transform(xml)

        out_path = os.path.join(RESULT_DIR, file.replace(".xml", "_out.xml"))
        with open(out_path, "wb") as f:
            f.write(etree.tostring(result, pretty_print=True))

def merge_results():
    print("\n[3/4] Scalanie wyników w finalny plik...")

    files = sorted([f for f in os.listdir(RESULT_DIR) if f.endswith("_out.xml")])

    with open(FINAL_OUTPUT, "wb") as out:
        out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write(
            b'<rss xmlns:g="http://base.google.com/ns/1.0" '
            b'xmlns:iaiext="http://www.iai-shop.com/developers/iof/extensions.phtml" '
            b'xmlns:php="http://php.net/xsl" version="2.0">\n'
        )
        out.write(b'<channel>\n')

        for file in tqdm(files, desc="Łączenie wyników", unit="plik"):
            path = os.path.join(RESULT_DIR, file)
            tree = etree.parse(path)
            root = tree.getroot()

            for item in root.xpath("//item"):
                clean = etree.Element("item")
                clean.text = item.text

                for child in item:
                    clean.append(child)

                out.write(etree.tostring(clean, encoding="utf-8"))
                out.write(b"\n")

        out.write(b'</channel>\n</rss>')

def cleanup():
    print("\n[4/4] Usuwanie plików tymczasowych...")

    shutil.rmtree(CHUNK_DIR, ignore_errors=True)
    shutil.rmtree(RESULT_DIR, ignore_errors=True)

def main():
    try:
        input_file = find_input_file()

        if not confirm_file(input_file):
            sys.exit(1)

        chunk_xml(input_file)
        transform_chunks()
        merge_results()
        cleanup()

    except Exception as e:
        print("\nWystąpił BŁĄD!")
        print("Szczegóły:", str(e))
        print("\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
