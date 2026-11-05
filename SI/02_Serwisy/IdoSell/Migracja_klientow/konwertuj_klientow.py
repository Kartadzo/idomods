# -*- coding: utf-8 -*-
"""
Konwersja eksportu klientów (*.client*.csv) na CSV importu klientów IdoSell.

Panel IdoSell zeruje cały rekord, gdy w pliku jest choć jedna kolumna spoza
specyfikacji (krok mapowania), dlatego wyjście zawiera wyłącznie kolumny IdoSell.

Użycie: python konwertuj_klientow.py [plik_wejściowy]
Bez argumentu bierze jedyny plik *.client*.csv z folderu źródło/.
"""
import csv
import glob
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
ZRODLO = os.path.join(FOLDER, "źródło")
WYNIK = os.path.join(FOLDER, "wynik")

KOLUMNY = [
    "login", "email", "firstname", "lastname", "street", "zipcode", "city",
    "country", "phone", "companyname", "taxidnumber", "date_of_registration", "rebate",
]

# ISO 3166-1 alpha-2 -> polska nazwa kraju (format pola country w IdoSell)
KRAJE = {
    "AT": "Austria", "AU": "Australia", "BE": "Belgia", "BG": "Bułgaria",
    "BR": "Brazylia", "BY": "Białoruś", "CH": "Szwajcaria", "CO": "Kolumbia",
    "CY": "Cypr", "CZ": "Czechy", "DE": "Niemcy", "DK": "Dania",
    "EE": "Estonia", "ES": "Hiszpania", "ET": "Etiopia", "FI": "Finlandia",
    "FR": "Francja", "GB": "Wielka Brytania", "GE": "Gruzja", "GF": "Gujana Francuska",
    "GG": "Guernsey", "GP": "Gwadelupa", "GR": "Grecja", "HK": "Hongkong",
    "HR": "Chorwacja", "HU": "Węgry", "IE": "Irlandia", "IL": "Izrael",
    "IS": "Islandia", "IT": "Włochy", "KR": "Korea Południowa", "LI": "Liechtenstein",
    "LT": "Litwa", "LU": "Luksemburg", "LV": "Łotwa", "MA": "Maroko",
    "MQ": "Martynika", "MT": "Malta", "MY": "Malezja", "NC": "Nowa Kaledonia",
    "NL": "Holandia", "NO": "Norwegia", "NZ": "Nowa Zelandia", "PL": "Polska",
    "PT": "Portugalia", "RE": "Reunion", "RO": "Rumunia", "RS": "Serbia",
    "SA": "Arabia Saudyjska", "SE": "Szwecja", "SI": "Słowenia", "SK": "Słowacja",
    "TN": "Tunezja", "TR": "Turcja", "TW": "Tajwan", "UA": "Ukraina",
    "US": "Stany Zjednoczone", "ZA": "Republika Południowej Afryki",
}

POLA_ADRESU = ("street_1", "street_2", "city", "zip_code", "country_code", "phone", "company_name", "tax_id")


def wybierz_plik():
    if len(sys.argv) > 1:
        return sys.argv[1]
    pliki = sorted(glob.glob(os.path.join(ZRODLO, "*.client*.csv")))
    pliki = [p for p in pliki if not os.path.basename(p).startswith("test.")]
    if len(pliki) == 1:
        return pliki[0]
    print("Znaleziono pliki:" if pliki else "Brak pliku *.client*.csv w folderze źródło.")
    for i, p in enumerate(pliki, 1):
        print(f"  {i}. {os.path.basename(p)}")
    if not pliki:
        sys.exit(1)
    nr = input("Numer pliku: ").strip()
    return pliki[int(nr) - 1]


def adresy(wiersz):
    """Zwraca listę bloków adresowych (słowniki) z niepustą treścią."""
    wynik = []
    n = 1
    while f"street_1 {n}" in wiersz:
        blok = {pole: (wiersz.get(f"{pole} {n}") or "").strip() for pole in POLA_ADRESU}
        blok["default"] = (wiersz.get(f"address_default {n}") or "").strip()
        if any(blok[p] for p in ("street_1", "city", "zip_code")):
            wynik.append(blok)
        n += 1
    return wynik


def main():
    wejscie = wybierz_plik()
    os.makedirs(WYNIK, exist_ok=True)
    wyjscie = os.path.join(WYNIK, "import_klientow_idosell.csv")
    raport = os.path.join(WYNIK, "raport.csv")

    widziane = set()
    licz = {"zapisano": 0, "duplikat": 0, "bez_adresu": 0, "nieznany_kraj": 0}

    with open(wejscie, encoding="utf-8-sig", newline="") as fin, \
            open(wyjscie, "w", encoding="utf-8", newline="") as fout, \
            open(raport, "w", encoding="utf-8", newline="") as frap:
        czytnik = csv.DictReader(fin)
        czytnik.fieldnames = [h.strip() for h in czytnik.fieldnames]
        pisz = csv.DictWriter(fout, fieldnames=KOLUMNY, lineterminator="\r\n")
        pisz.writeheader()
        rap = csv.writer(frap, lineterminator="\r\n")
        rap.writerow(["email", "powod", "szczegoly"])

        for w in czytnik:
            email = (w.get("email") or "").strip()
            klucz = email.lower()
            if klucz in widziane:
                licz["duplikat"] += 1
                rap.writerow([email, "duplikat_email", "pominięto, zostaje pierwszy wiersz"])
                continue
            widziane.add(klucz)

            lista = adresy(w)
            adr = next((a for a in lista if a["default"] == "1"), lista[0] if lista else None)
            rabat = (w.get("discount") or "").strip()
            rekord = {
                "login": email,
                "email": email,
                "firstname": (w.get("first_name") or "").strip(),
                "lastname": (w.get("last_name") or "").strip(),
                "date_of_registration": (w.get("date_add") or "").strip(),
                "rebate": "" if rabat in ("", "0", "0.00") else rabat,
            }
            if adr:
                kod = adr["country_code"].upper()
                kraj = KRAJE.get(kod, "")
                if kod and not kraj:
                    licz["nieznany_kraj"] += 1
                    rap.writerow([email, "nieznany_kod_kraju", kod])
                rekord.update({
                    "street": " ".join(x for x in (adr["street_1"], adr["street_2"]) if x),
                    "zipcode": adr["zip_code"],
                    "city": adr["city"],
                    "country": kraj,
                    "phone": adr["phone"],
                    "companyname": adr["company_name"],
                    "taxidnumber": adr["tax_id"],
                })
            else:
                licz["bez_adresu"] += 1
            pisz.writerow(rekord)
            licz["zapisano"] += 1

    print(f"Wejście:  {os.path.basename(wejscie)}")
    print(f"Wyjście:  {wyjscie}")
    print(f"Zapisano klientów: {licz['zapisano']}")
    print(f"  w tym bez adresu: {licz['bez_adresu']}")
    print(f"Pominięte duplikaty e-mail: {licz['duplikat']}")
    print(f"Nieznane kody kraju: {licz['nieznany_kraj']}")
    print(f"Raport: {raport}")


if __name__ == "__main__":
    main()
