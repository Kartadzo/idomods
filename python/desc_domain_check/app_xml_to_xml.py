#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re
from urllib.parse import urlparse

# Ścieżka do pliku CSV
CSV_FILE = "dane.csv"

# Wyrażenie regularne do wyłuskania linków z HTML
# obsługuje href w różnych cudzysłowach i protokoły http(s)
URL_REGEX = re.compile(
    r'https?://[^\s"\'<>]+',
    re.IGNORECASE
)

domeny = set()

with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        # przechodzimy kolumny od B dalej (indeks 1+)
        for cell in row[1:]:
            if not cell:
                continue
            # znajdź wszystkie linki w komórce
            for match in URL_REGEX.findall(cell):
                domena = urlparse(match).netloc.lower()
                domeny.add(domena)

# wypisz unikalne domeny
for d in sorted(domeny):
    print(d)
