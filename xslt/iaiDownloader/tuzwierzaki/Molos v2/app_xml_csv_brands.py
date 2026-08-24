#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import io
import socket
import struct
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.connection import HTTPConnection
from lxml import etree

xml_url    = 'https://b2b.molos.com.pl/xml/bdc7f794385b9abb15db0fd437cab357/products.xml'
xslt_file  = 'synch_template_brands.xml'
out_xml    = 'output.xml'
out_csv    = 'output.csv'
record_tag = 'item'

def configure_keepalive():
    """
    Ustawia TCP Keep-Alive w zależności od platformy.
    """
    # zawsze włączamy SO_KEEPALIVE
    HTTPConnection.default_socket_options += [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    ]

    if sys.platform.startswith('linux'):
        HTTPConnection.default_socket_options += [
            (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE,  30),
            (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
            (socket.IPPROTO_TCP, socket.TCP_KEEPCNT,   6),
        ]
    elif sys.platform == 'darwin':
        HTTPConnection.default_socket_options += [
            (socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, 30),
        ]
    elif sys.platform.startswith('win'):
        # Windows – ustaw parametry przez IOCTL
        SIO_KEEPALIVE_VALS = 0x98000004
        # keepalive: on, idle=seconds, interval=seconds (ms)
        keepalive_vals = struct.pack('III', 1, 30 * 1000, 10 * 1000)
        # patch na globalny adapter
        orig_connect = HTTPConnection.connect

        def connect_with_keepalive(self):
            sock = self.socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.ioctl(SIO_KEEPALIVE_VALS, keepalive_vals)
            return orig_connect(self)

        HTTPConnection.connect = connect_with_keepalive

# —————— START ——————
# Włącz keep-alive przed mountowaniem adapterów
configure_keepalive()

parser = etree.XMLParser(encoding='utf-8', recover=True)

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

try:
    headers = {
        "User-Agent": "XMLFetcher/1.0",
        "Connection": "keep-alive"
    }
    resp = session.get(xml_url, headers=headers, timeout=(5, 60), stream=True)
    resp.raise_for_status()

    buf = io.BytesIO()
    for chunk in resp.iter_content(chunk_size=8*1024):
        if chunk:
            buf.write(chunk)
    buf.seek(0)

    xml_tree = etree.parse(buf, parser)
    print(f"Pobrano i sparsowano XML z: {xml_url}")
except Exception as e:
    print(f"Błąd pobierania/parowania XML z URL: {e}", file=sys.stderr)
    sys.exit(1)

try:
    xslt_tree = etree.parse(xslt_file, parser)
    print(f"Wczytano szablon XSLT: {xslt_file}")
except (OSError, etree.XMLSyntaxError) as e:
    print(f"Błąd wczytywania XSLT: {e}", file=sys.stderr)
    sys.exit(1)

transform   = etree.XSLT(xslt_tree)
result_tree = transform(xml_tree)

# Zapisz wynikowy XML
xml_bytes = etree.tostring(
    result_tree,
    pretty_print=True,
    xml_declaration=True,
    encoding='utf-8'
)
os.makedirs(os.path.dirname(out_xml) or '.', exist_ok=True)
with open(out_xml, 'wb') as f:
    f.write(xml_bytes)
print(f"Wynik XML zapisano w: {out_xml}")

# Parsowanie rekordów <record_tag>
root    = result_tree.getroot()
records = root.xpath(f'.//*[local-name()="{record_tag}"]')
print(f"Znaleziono {len(records)} elementów <{record_tag}>")

if not records:
    open(out_csv, 'w', encoding='utf-8').close()
    print(f"Nie znaleziono <{record_tag}>, utworzono pusty: {out_csv}")
    sys.exit(0)

# Nagłówki CSV z unikalnych tagów pierwszego rekordu
columns = []
seen    = set()
for child in records[0]:
    col = child.tag.split('}', 1)[-1]
    if col not in seen:
        seen.add(col)
        columns.append(col)

os.makedirs(os.path.dirname(out_csv) or '.', exist_ok=True)
with open(out_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(columns)
    for rec in records:
        row = []
        for col in columns:
            nodes = rec.xpath(f'./*[local-name()="{col}"]')
            el    = nodes[0] if nodes else None
            row.append((el.text or '').strip() if el is not None else '')
        writer.writerow(row)

print(f"Wynik CSV zapisano w: {out_csv}")
