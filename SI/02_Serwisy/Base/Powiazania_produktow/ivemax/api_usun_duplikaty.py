"""Usuwa duplikaty towarów powstałe przy imporcie nowych towarów 2026-10-21 (decyzja użytkownika).

Grupy: towary z identyczną nazwą PL, ceną i długością opisu w zakresie ID importu.
W grupie zostaje towar z kodem zewnętrznym; z kilku o tym samym kodzie zewnętrznym zostaje
ten z kodem producenta (lepsze dane). Usuwany jest tylko towar ukryty i dodany podczas
importu (OKNO_IMPORTU). Towary o tej samej nazwie, ale innej cenie (osobne produkty
Shoparena) zostają. Kody producenta przenosi potem api_nowe_towary_naprawa.py.

Uruchomienie: python api_usun_duplikaty.py (pokazuje listę i pyta), --bez-pytania.
"""

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

from api_kod_producenta import KlientApi, PLIK_KONFIGURACJI, FOLDER_WYNIKOW
from api_nowe_towary import bledy_z

ZAKRES_ID = range(4643, 4990)
OKNO_IMPORTU = ("2026-10-21 18:05:00", "2026-10-21 18:40:00")
ROZMIAR_ODCZYTU = 50


def opis_towaru(t: dict) -> dict:
    """Wyciąga pola potrzebne do porównania duplikatów."""
    rozmiar = (t.get("productSizesAttributes") or [{}])[0]
    pol = next(x for x in t["productDescriptionsLangData"] if x["langId"] == "pol")
    return {
        "id": t["productId"], "nazwa": pol["productName"].strip(),
        "opis_dl": len(pol.get("productLongDescription", "")), "cena": t.get("productRetailPrice"),
        "zew": (rozmiar.get("productSizeCodeExternal") or "").strip(),
        "kod": (rozmiar.get("productSizeCodeProducer") or "").strip(),
        "dodano": t.get("productAddingTime", ""), "widoczny": t.get("productIsVisible"),
    }


def main() -> int:
    """Wyznacza duplikaty do usunięcia, pyta o zgodę, usuwa i weryfikuje."""
    with open(PLIK_KONFIGURACJI, encoding="utf-8") as plik:
        konf = json.load(plik)
    os.makedirs(FOLDER_WYNIKOW, exist_ok=True)
    sciezka = os.path.join(FOLDER_WYNIKOW,
                           f"api_usun_duplikaty_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}")
    with open(sciezka + ".jsonl", "w", encoding="utf-8") as dziennik:
        api = KlientApi(konf["domena"], konf["klucz_api"], dziennik)
        towary = []
        ids = list(ZAKRES_ID)
        for start in range(0, len(ids), ROZMIAR_ODCZYTU):
            odp = api.zapytanie("GET", "products/products?productIds=" +
                                ",".join(map(str, ids[start:start + ROZMIAR_ODCZYTU])))
            towary += [opis_towaru(t) for t in odp.get("results") or []]

        grupy = defaultdict(list)
        for t in towary:
            grupy[(t["nazwa"], t["cena"], t["opis_dl"])].append(t)
        do_usuniecia = []
        for grupa in grupy.values():
            if len(grupa) < 2:
                continue
            z_kodem = [t for t in grupa if t["zew"]]
            if not z_kodem:
                continue
            zostaje = {}
            for t in z_kodem:
                obecny = zostaje.get(t["zew"])
                if obecny is None or (t["kod"] and not obecny["kod"]):
                    zostaje[t["zew"]] = t
            for t in grupa:
                if t in zostaje.values():
                    continue
                if not (OKNO_IMPORTU[0] <= t["dodano"] <= OKNO_IMPORTU[1]) or t["widoczny"] != "n":
                    print(f"  pomijam {t['id']}: spoza importu albo widoczny")
                    continue
                t["zamiast"] = ", ".join(str(z["id"]) for z in zostaje.values())
                do_usuniecia.append(t)

        print(f"Do usunięcia: {len(do_usuniecia)}")
        for t in do_usuniecia:
            print(f"  {t['id']} (kod zew. '{t['zew']}', kod prod. '{t['kod']}') → zostaje {t['zamiast']}")
        if not do_usuniecia or ("--bez-pytania" not in sys.argv and
                                input("Usunąć? [t/N]: ").strip().lower() != "t"):
            return 0

        odp = api.zapytanie("POST", "products/products/delete", {"params": {"products": [
            {"productId": t["id"]} for t in do_usuniecia]}})
        bledy = bledy_z((odp.get("results") or {}).get("faults") if isinstance(odp.get("results"), dict)
                        else None)
        pozostale = set()
        ids_usuwane = [t["id"] for t in do_usuniecia]
        for start in range(0, len(ids_usuwane), ROZMIAR_ODCZYTU):
            sprawdz = api.zapytanie("GET", "products/products?productIds=" +
                                    ",".join(map(str, ids_usuwane[start:start + ROZMIAR_ODCZYTU])))
            pozostale |= {t["productId"] for t in sprawdz.get("results") or []
                          if t.get("productIsDeleted") != "y"}

    with open(sciezka + ".csv", "w", encoding="utf-8-sig", newline="") as plik:
        pisarz = csv.writer(plik)
        pisarz.writerow(["id_usuniety", "nazwa", "kod_zewnetrzny", "kod_producenta", "zostaje", "wynik"])
        for t in do_usuniecia:
            pisarz.writerow([t["id"], t["nazwa"], t["zew"], t["kod"], t["zamiast"],
                             "NIE USUNIĘTO" if t["id"] in pozostale else "usunięto"])
    print(f"Usunięto: {len(do_usuniecia) - len(pozostale)}, nie usunięto: {sorted(pozostale)} {bledy}")
    print(f"Dziennik: {sciezka}.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
