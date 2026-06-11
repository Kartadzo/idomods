#!/usr/bin/env python3
"""
Skrypt filtruje plik XLIFF 1.2 i usuwa wszystkie <trans-unit>,
w których zawartość <source> i <target> nie jest identyczna.
Pozostawi tylko te trans-unit, gdzie source.text == target.text.
"""

from lxml import etree
import sys

XLIF_NAMESPACE = "urn:oasis:names:tc:xliff:document:1.2"
NSMAP = {"xliff": XLIF_NAMESPACE}

def filter_identical_units(input_path: str, output_path: str) -> None:
    # Wczytaj cały dokument XLIFF
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()

    # Przechodzimy po wszystkich trans-unit w przestrzeni nazw XLIFF
    xpath_expr = ".//xliff:trans-unit"
    for unit in root.xpath(xpath_expr, namespaces=NSMAP):
        src_elem = unit.find("xliff:source", namespaces=NSMAP)
        tgt_elem = unit.find("xliff:target", namespaces=NSMAP)

        src_text = (src_elem.text or "").strip()
        tgt_text = (tgt_elem.text or "").strip()

        # Jeśli source != target, usuwamy ten <trans-unit>
        if src_text != tgt_text:
            parent = unit.getparent()
            parent.remove(unit)

    # Zapisz wynik do nowego pliku
    tree.write(
        output_path,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )

def main():
    if len(sys.argv) != 3:
        print("Użycie: python3 filter_xliff.py <wejście.xliff> <wyjście.xliff>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    filter_identical_units(input_file, output_file)
    print(f"Zapisano przefiltrowany XLIFF do: {output_file}")

if __name__ == "__main__":
    main()
