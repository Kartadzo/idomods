#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import os
import glob
import re
from datetime import datetime

def find_input_files():
    """
    Jeśli użytkownik poda dwa pliki CSV jako argumenty,
    traktujemy je kolejno jako orders_file i products_file.
    W przeciwnym razie autodetekcja w bieżącym katalogu:
      - orders: plik z nagłówkiem 'orderId;'
      - products: plik z nagłówkiem '@id,'
    """
    if len(sys.argv) == 3:
        return sys.argv[1], sys.argv[2]

    csvs = glob.glob(os.path.join(os.getcwd(), '*.csv'))
    orders_file = products_file = None
    for f in csvs:
        with open(f, newline='', encoding='utf-8-sig') as fp:
            header = fp.readline()
            if header.startswith('orderId;'):
                orders_file = f
            elif header.startswith('@id,'):
                products_file = f
    if not orders_file or not products_file:
        print("Nie znaleziono plików wejściowych. Podaj:\n"
              "  1) orders.csv  2) products.csv")
        sys.exit(1)
    print(f"Orders file:  {orders_file}")
    print(f"Products file:{products_file}")
    return orders_file, products_file


def load_product_mapping(products_csv):
    """
    Wczytuje plik products_csv (delimiter=',') o nagłówku:
      @id,/price@gross,/description/name[pol]
    Zwraca dict: { id_str: {'price': float, 'name': str} }
    """
    mapping = {}
    with open(products_csv, newline='', encoding='utf-8-sig') as fp:
        reader = csv.DictReader(fp, delimiter=',')
        for row in reader:
            pid = row['@id'].strip()
            price = row.get('/price@gross', '').strip()
            name  = row.get('/description/name[pol]', '').strip()
            try:
                price_f = float(price.replace(',', '.'))
            except:
                price_f = 0.0
            mapping[pid] = {'price': price_f, 'name': name}
    return mapping


def parse_sku_list(sku_field):
    """
    Rozbija pole sku_field, np:
      "12801 (1 szt.),14136 (10 szt.)"
    Zwraca listę krotek (sku_id, quantity:int).
    Jeśli brak '(n szt.)' przy sku, quantity=n.
    """
    parts = [p.strip() for p in sku_field.split(',') if p.strip()]
    result = []
    for part in parts:
        # szukamy id (ciąg cyfr na początku)
        m_id = re.match(r'(\d+)', part)
        sku_id = m_id.group(1) if m_id else ''
        # szukamy ilości w nawiasie
        m_qty = re.search(r'\((\d+)', part)
        qty = int(m_qty.group(1)) if m_qty else 1
        if sku_id:
            result.append((sku_id, qty))
    return result


def load_orders(orders_csv):
    """
    Wczytuje plik orders_csv (delimiter=';') i zwraca listę dictów.
    """
    with open(orders_csv, newline='', encoding='utf-8-sig') as fp:
        reader = csv.DictReader(fp, delimiter=';')
        return list(reader)


def format_recorded_at(timestamp_str):
    """
    Z wejściowego 'recordedAt' (np. '2025-03-26' lub '2025-03-26 14:30:00')
    zwraca ISO 8601 z 'Z', np. '2025-03-26T00:00:00Z'
    lub '2025-03-26T14:30:00Z'.
    """
    # próbujemy dwie najczęstsze struktury
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    # fallback: zwracamy oryginał
    return timestamp_str


def process_and_export(orders, prod_map, output_file):
    """
    orders: lista dictów z zamówieniami
    prod_map: {sku: {'price': float, 'name': str}}
    """
    # pamięć cen jednostkowych value.amount
    unit_value_map = {}

    fields = [
      'orderId','client.email','recordedAt','paymentInfo.method',
      'products.finalUnitPrice.amount','products.finalUnitPrice.currency',
      'products.name','products.quantity','products.sku',
      'revenue.amount','revenue.currency',
      'value.amount','value.currency'
    ]
    with open(output_file, 'w', newline='', encoding='utf-8') as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, delimiter=';')
        writer.writeheader()

        for o in orders:
            # parsujemy listę SKU z ilościami
            sku_list = parse_sku_list(o['products.sku'])

            # oryginalne wartości, jako float
            orig_rev_amt   = float(o['revenue.amount'].replace(',', '.'))
            orig_rev_curr  = o['revenue.currency']
            orig_val_amt   = float(o['value.amount'].replace(',', '.'))
            orig_val_curr  = o['value.currency']

            # sformatowany 'recordedAt' do ISO 8601
            recorded_iso = format_recorded_at(o['recordedAt'])

            # Jeśli jest tylko jeden SKU w wierszu – nie dzielimy:
            if len(sku_list) == 1:
                sku, qty = sku_list[0]
                # zapamiętujemy cenę jednostkową z value.amount
                unit_value_map[sku] = orig_val_amt / qty

                # genereujemy wiersz
                out = {
                  'orderId': o['orderId'],
                  'client.email': o['client.email'],
                  'recordedAt': recorded_iso,
                  'paymentInfo.method': o['paymentInfo.method'],
                  # final unit price wrzucamy tak jak poprzednio
                  'products.finalUnitPrice.amount': f"{orig_rev_amt * 0.77:.2f}",
                  'products.finalUnitPrice.currency': o['products.finalUnitPrice.currency'],
                  # nazwa z mapowania produktów
                  'products.name': prod_map.get(sku, {}).get('name', ''),
                  'products.quantity': str(qty),
                  'products.sku': sku,
                  # revenue.amount – pozostaje oryginalne
                  'revenue.amount': f"{orig_rev_amt:.2f}",
                  'revenue.currency': orig_rev_curr,
                  # value.amount – przepisujemy oryginał
                  'value.amount': f"{orig_val_amt:.2f}",
                  'value.currency': orig_val_curr
                }
                writer.writerow(out)
                continue

            # W przeciwnym razie – dzielimy na każdy SKU osobno
            for sku, qty in sku_list:
                prod        = prod_map.get(sku, {'price': 0.0, 'name': ''})
                unit_price  = prod['price']
                name        = prod['name']

                # revenue.amount = cena brutto z products * qty
                rev_amt = unit_price * qty

                # wartość value.amount
                if sku in unit_value_map:
                    # używamy wcześniej zapamiętanej ceny jednostkowej
                    val_amt = unit_value_map[sku] * qty
                else:
                    # wyliczamy i zapisujemy nową cenę jednostkową
                    val_amt = unit_price * qty
                    unit_value_map[sku] = unit_price

                # final unit price – bazujemy na oryginalnym revenue*
                final_unit = val_amt * 0.77

                # wartość value.amount
                if sku in unit_value_map:
                    # używamy wcześniej zapamiętanej ceny jednostkowej
                    val_amt = unit_value_map[sku] * qty
                else:
                    # wyliczamy i zapisujemy nową cenę jednostkową
                    val_amt = unit_price * qty
                
                out = {
                  'orderId': o['orderId'],
                  'client.email': o['client.email'],
                  'recordedAt': recorded_iso,
                  'paymentInfo.method': o['paymentInfo.method'],
                  'products.finalUnitPrice.amount': f"{final_unit:.2f}",
                  'products.finalUnitPrice.currency': o['products.finalUnitPrice.currency'],
                  'products.name': name,
                  'products.quantity': qty,
                  'products.sku': sku,
                  'revenue.amount': f"{rev_amt:.2f}",
                  'revenue.currency': orig_rev_curr,
                  'value.amount': f"{val_amt:.2f}",
                  'value.currency': orig_val_curr
                }
                writer.writerow(out)

    print(f"Wynik zapisano w: {output_file}")



def main():
    orders_csv, products_csv = find_input_files()
    prod_map = load_product_mapping(products_csv)
    orders   = load_orders(orders_csv)

    output_file = 'przetworzony_plik_zamowien.csv'
    process_and_export(orders, prod_map, output_file)


if __name__ == '__main__':
    main()
