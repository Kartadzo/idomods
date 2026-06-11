#!/usr/bin/env python3
"""
filter_columns.py
Filtrowanie kolumn CSV z obsługą wersji językowych.

Przykład:
python filter_columns.py --input raw.csv --output out.csv \
  --cols "@id,/sizes/size@code_external,@currency,@code_producer,/producer@name,/category@name[lang],/unit@id,/series@name[lang],/price@gross,/price@net,/price@vat,/srp@gross,/srp@net,/srp@vat,/price_wholesale/site@gross,/price_wholesale/site@net,/price_wholesale/site@vat,/price_wholesale/site@id,/price_minimal/site@gross,/price_minimal/site@net,/price_minimal/site@vat,/price_minimal/site@id,/price_retail/site@gross,/price_retail/site@net,/price_retail/site@vat,/price_retail/site@id,/price_retail/site@size_id,/pricecomparator_price/site@gross,/pricecomparator_price/site@net,/pricecomparator_price/site@vat,/pricecomparator_price/site@id,/pricecomparator_price/site@service_id,/sizes/size@code_producer,/sizes/size@weight,/sizes/size/price@gross,/sizes/size/price@net,/delivery_time/mode@type,/delivery_time/time@days,/sum_in_basket@value,/images/large/image@url,/images/icons/icon@url,/images/icons/auction_icon@url,/images/icons/group_icon@url,/associated_products/product@id,/hotspots/site@id,/hotspots/site@manual_config,/hotspots/site/promotion@visible,/hotspots/site/discount@visible,/hotspots/site/distinguished@visible,/hotspots/site/special@visible,/enable_in_pos@enabled,/taxcode,/availability_profile@id,/availability_management@value,/loyalty_program/site@id,/loyalty_program/site@operation,/loyalty_program/site@clients,/loyalty_program/site@points,/advance@rate,/priority@level,/sell_by/retail@quantity,/sell_by/wholesale@quantity,/inwrapper@quantity,/visibility/site@visible,/visibility/price_comparator@visible,/availability/site@id,/availability/site@value,/note,/deliverer@id,/description/name[lang],/description/short_desc[lang],/description/long_desc[lang],/description/pricecomparator_name[lang],/description/meta_title[lang],/description/meta_description[lang],/description/meta_keywords[lang],/parameters/parameter@textid[lang],/parameters/parameter@distinction,/parameters/parameter@group_distinction,/parameters/parameter@projector_hide,/prices_configuration_for_shops@value,/size_chart@id,/size_chart@name[lang],/group@id,/group/group_by_parameter@name[lang],/group/group_by_parameter/product_value@name[lang]" \
  --langs pol,lit,cze,hun,slo
"""

import argparse
import sys
import pandas as pd
from typing import List, Tuple

def parse_args():
    p = argparse.ArgumentParser(description="Filter CSV columns with language variants")
    p.add_argument("--input", "-i", required=True, help="Wejściowy plik CSV")
    p.add_argument("--output", "-o", required=True, help="Wyjściowy plik CSV")
    p.add_argument("--cols", "-c", required=True,
                   help="Lista kolumn do wybrania (przecinek-separated) lub ścieżka do pliku z listą kolumn")
    p.add_argument("--langs", "-l", default="", help="Lista języków rozdzielona przecinkami, np. lang,lit")
    p.add_argument("--sep", default=",", help="Separator CSV (domyślnie ',')")
    p.add_argument("--encoding", default="utf-8", help="Kodowanie plików (domyślnie utf-8)")
    p.add_argument("--warn-missing", action="store_true", help="Wypisz ostrzeżenia o brakujących kolumnach")
    return p.parse_args()

def load_requested_columns(cols_arg: str) -> List[str]:
    """Jeśli cols_arg to ścieżka do pliku, wczytaj go; w przeciwnym razie rozbij po przecinkach."""
    try:
        # spróbuj otworzyć jako plik
        with open(cols_arg, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            # plik może zawierać kolumny w jednej linii rozdzielone przecinkami lub po linii
            if len(lines) == 1 and "," in lines[0]:
                return [c.strip() for c in lines[0].split(",") if c.strip()]
            return lines
    except FileNotFoundError:
        # traktuj jako lista przecinkowa
        return [c.strip() for c in cols_arg.split(",") if c.strip()]

def expand_columns_for_langs(requested: List[str], langs: List[str]) -> List[str]:
    """
    Rozszerza listę żądanych kolumn:
    - jeśli kolumna zawiera '[lang]' -> zastępuje go wszystkimi językami z langs
    - jeśli kolumna zawiera '[pol]' (konkretna) -> zostawia bez zmian
    - jeśli kolumna nie zawiera nawiasów -> zostawia bez zmian
    Zwraca listę w kolejności wejściowej (rozszerzona).
    """
    out = []
    for col in requested:
        if "[lang]" in col:
            if not langs:
                # brak języków -> zostaw placeholder (użytkownik powinien podać langs)
                out.append(col)
            else:
                for L in langs:
                    out.append(col.replace("[lang]", f"[{L}]"))
        else:
            # jeśli kolumna ma już [pol] lub [lit] itp. -> dodaj bez zmian
            out.append(col)
    return out

def find_available_columns(df_cols: List[str], desired_cols: List[str]) -> Tuple[List[str], List[str]]:
    """
    Dla każdej desired col szuka dokładnego dopasowania w df_cols.
    Jeśli nie znajdzie, próbuje wariantów (np. bez sufiksu językowego).
    Zwraca (found_list_in_order, missing_list).
    """
    found = []
    missing = []
    cols_set = set(df_cols)
    for d in desired_cols:
        if d in cols_set:
            found.append(d)
            continue
        # spróbuj usunąć ewentualne [lang] lub [pol] -> dopasuj bez sufiksu
        # np "/category@name[pol]" -> "/category@name"
        if "[" in d and d.endswith("]"):
            base = d[:d.rfind("[")]
            if base in cols_set:
                found.append(base)
                continue
        # spróbuj dopasować warianty z/bez prefixów (czasem w raw są inne nazwy)
        # tutaj można dodać dodatkowe heurystyki, np. zamiana 'card@url[pol]' -> 'card@url'
        # jeśli nic nie pasuje -> oznacz jako missing
        missing.append(d)
    return found, missing

def main():
    args = parse_args()
    requested = load_requested_columns(args.cols)
    langs = [l.strip() for l in args.langs.split(",") if l.strip()] if args.langs else []
    expanded = expand_columns_for_langs(requested, langs)

    # Wczytaj CSV surowy
    try:
        df = pd.read_csv(args.input, sep=args.sep, dtype=str, encoding=args.encoding, keep_default_na=False)
    except Exception as e:
        print(f"Błąd wczytywania pliku wejściowego: {e}", file=sys.stderr)
        sys.exit(2)

    df_cols = list(df.columns)
    # Znajdź kolumny dostępne w pliku
    found, missing = find_available_columns(df_cols, expanded)

    if args.warn_missing and missing:
        print("Ostrzeżenie: nie znaleziono następujących żądanych kolumn:", file=sys.stderr)
        for m in missing:
            print("  -", m, file=sys.stderr)

    if not found:
        print("Brak dopasowanych kolumn do zapisania. Nic nie zapisano.", file=sys.stderr)
        sys.exit(3)

    # Zachowaj kolejność zgodnie z expanded, ale tylko te które znaleziono (found może być subset)
    # find_available_columns zwraca found w kolejności przeszukiwania; upewnijmy się, że kolejność odpowiada expanded
    final_cols = [c for c in expanded if c in found or ( "[" in c and c[:c.rfind("[")] in found )]
    # Upewnij się, że kolumny istnieją w df (jeśli znaleźliśmy base bez sufiksu, użyj base)
    resolved_cols = []
    for c in final_cols:
        if c in df_cols:
            resolved_cols.append(c)
        elif "[" in c and c[:c.rfind("[")] in df_cols:
            resolved_cols.append(c[:c.rfind("[")])
        # else: pomiń

    # Usuń duplikaty zachowując kolejność
    seen = set()
    resolved_cols_unique = []
    for c in resolved_cols:
        if c not in seen:
            resolved_cols_unique.append(c)
            seen.add(c)

    # Zapisz wynik
    try:
        df_out = df.loc[:, resolved_cols_unique]
        df_out.to_csv(args.output, index=False, sep=args.sep, encoding=args.encoding)
        print(f"Zapisano {len(df_out.columns)} kolumn do {args.output}")
        if missing and args.warn_missing:
            print(f"Nie znaleziono {len(missing)} kolumn (szczegóły powyżej).", file=sys.stderr)
    except Exception as e:
        print(f"Błąd zapisu pliku wyjściowego: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()
