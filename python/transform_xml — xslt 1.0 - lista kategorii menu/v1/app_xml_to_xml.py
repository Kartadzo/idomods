import os
from lxml import etree
from tqdm import tqdm

XML_INPUT = "source.xml"
XSLT_FILE = "feediai_ceny_omnibus_for_xml.xslt"

def find_largest_xml(directory="."):
    """Zwraca ścieżkę do największego pliku XML w folderze."""
    xml_files = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".xml") and os.path.isfile(f)
    ]

    if not xml_files:
        raise FileNotFoundError("Brak plików XML w folderze.")

    largest = max(xml_files, key=lambda f: os.path.getsize(f))
    return largest

def main():
    # wybór pliku wejściowego
    if os.path.exists(XML_INPUT):
        xml_file = XML_INPUT
        print(f"Używam pliku wejściowego: {xml_file}")
    else:
        xml_file = find_largest_xml()
        print(f"Nie znaleziono source.xml — używam największego pliku: {xml_file}")

    # wczytywanie XML z paskiem postępu
    file_size = os.path.getsize(xml_file)
    print(f"Wczytywanie XML ({file_size/1024/1024:.2f} MB)...")

    with open(xml_file, "rb") as f:
        data = b""
        for chunk in tqdm(iter(lambda: f.read(1024 * 1024), b""), 
                          total=file_size // (1024 * 1024) + 1,
                          unit="MB",
                          desc="Postęp"):
            data += chunk

    xml = etree.fromstring(data)
    xslt = etree.parse(XSLT_FILE)

    print("Przetwarzanie XSLT...")
    transform = etree.XSLT(xslt)
    result = transform(xml)

    print("Zapisywanie output.xml...")
    with open("output.xml", "wb") as f:
        f.write(etree.tostring(result, pretty_print=True))

    print("Gotowe!")

if __name__ == "__main__":
    main()
