"""Naprawa towarów utworzonych przez api_nowe_towary.py: uzupełnia tylko braki.

Dla każdego kodu zewnętrznego z nowe_towary_shoparena.csv bierze towar o najniższym ID
i uzupełnia: zdjęcia (gdy brak — pobiera z Shoparena i wysyła jako base64, bo IdoSell
nie zdąża pobrać dużych oryginałów z URL), menu sklepu (gdy brak), kod producenta (gdy
pusty i wolny). Dublety (wyższe ID z tym samym kodem) tylko raportuje.
Szczegóły: ANALIZA_api_nowe_towary.md, sekcja „Wynik importu i naprawa”.
"""

import base64
import csv
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import datetime

from api_kod_producenta import KlientApi, PLIK_KONFIGURACJI, FOLDER_WYNIKOW
from api_nowe_towary import PLIK_TOWAROW, SKLEP_ID, MENU_ID, PREFIKS_MENU, bledy_z

ROZMIAR_STRONY = 100
ROZMIAR_ODCZYTU = 50


def stan_rozmiarow(api: KlientApi):
    """Zwraca (kod zewnętrzny -> lista ID, kod producenta -> ID, ID -> kod producenta)."""
    zewnetrzne, zajete, kody_towarow = {}, {}, {}
    strona = 0
    while True:
        odp = api.zapytanie(
            "GET", f"products/sizes?result::page={strona}&result::pageNumber={ROZMIAR_STRONY}")
        for towar in (odp.get("results") or {}).values():
            ident = int(towar["productId"])
            for r in towar.get("sizesResult", []):
                zew = (r.get("productSizeCodeExternal") or "").strip()
                kod = (r.get("productProducerCode") or "").strip()
                if zew:
                    zewnetrzne.setdefault(zew, []).append(ident)
                if kod:
                    zajete[kod] = ident
                    kody_towarow[ident] = kod
        strona += 1
        if strona >= int((odp.get("result") or {}).get("pageAll", 0)):
            return zewnetrzne, zajete, kody_towarow


def main() -> int:
    """Odczytuje stan, uzupełnia braki i zapisuje dziennik naprawy."""
    try:
        with open(PLIK_KONFIGURACJI, encoding="utf-8") as plik:
            konf = json.load(plik)
        with open(PLIK_TOWAROW, encoding="utf-8-sig", newline="") as plik:
            towary = list(csv.DictReader(plik))
    except (OSError, ValueError) as blad:
        print(f"Błąd odczytu danych wejściowych: {blad}")
        return 1
    os.makedirs(FOLDER_WYNIKOW, exist_ok=True)
    sciezka = os.path.join(FOLDER_WYNIKOW,
                           f"api_nowe_towary_naprawa_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}")
    wiersze = []
    with open(sciezka + ".jsonl", "w", encoding="utf-8") as dziennik:
        api = KlientApi(konf["domena"], konf["klucz_api"], dziennik)
        print("Odczyt stanu sklepu…")
        zewnetrzne, zajete, kody_towarow = stan_rozmiarow(api)
        # products/sizes jeszcze jakiś czas zwraca usunięte towary — istnienie sprawdzam
        # w products/products (usuniętych nie zwraca albo mają productIsDeleted = y).
        kody_nowych = {w["kod_producenta"].strip() for w in towary if w["kod_producenta"].strip()}
        do_sprawdzenia = sorted({i for w in towary for i in zewnetrzne.get(w["kod_zewnetrzny"], [])}
                                | {zajete[k] for k in kody_nowych if k in zajete})
        szczegoly = {}
        for start in range(0, len(do_sprawdzenia), ROZMIAR_ODCZYTU):
            paczka = do_sprawdzenia[start:start + ROZMIAR_ODCZYTU]
            odp = api.zapytanie("GET", "products/products?productIds=" + ",".join(map(str, paczka)))
            for t in odp.get("results") or []:
                if t.get("productIsDeleted") != "y":
                    szczegoly[int(t["productId"])] = t
        zajete = {k: i for k, i in zajete.items() if i in szczegoly or k not in kody_nowych}
        kody_towarow = {i: k for i, k in kody_towarow.items() if i in szczegoly}
        plan = []
        for w in towary:
            ids = sorted(i for i in zewnetrzne.get(w["kod_zewnetrzny"], []) if i in szczegoly)
            plan.append((w, ids))

        for nr, (w, ids) in enumerate(plan, 1):
            print(f"\r  towar {nr}/{len(plan)}", end="")
            wpis = {"kod": w["kod_zewnetrzny"], "id": ids[0] if ids else "", "zrobiono": [],
                    "bledy": [], "dublety": ids[1:]}
            wiersze.append(wpis)
            if not ids:
                wpis["bledy"].append("brak towaru w sklepie")
                continue
            ident = ids[0]
            t = szczegoly.get(ident, {})
            zdjecia = [w[f"images {i}"] for i in range(1, 10) if w.get(f"images {i}", "").strip()]
            if zdjecia and not t.get("productImagesCount"):
                try:
                    dane = [base64.b64encode(urllib.request.urlopen(u, timeout=180).read()).decode()
                            for u in zdjecia]
                except OSError as blad:
                    wpis["bledy"].append(f"pobieranie zdjęć: {blad}")
                    dane = []
                if dane:
                    odp = api.zapytanie("PUT", "products/products", {"params": {
                        "picturesSettings": {"picturesSettingInputType": "base64",
                                             "picturesSettingOverwrite": "n",
                                             "picturesSettingScaling": "y"},
                        "products": [{"productId": ident, "productPictures": [
                            {"productPictureSource": d, "shopId": SKLEP_ID} for d in dane]}]}})
                    blad = "; ".join(bledy_z(r.get("faults")) for r in
                                     ((odp.get("results") or {}).get("productsResults") or []))
                    (wpis["bledy"] if blad.strip("; ") else wpis["zrobiono"]).append(
                        f"zdjęcia: {blad}" if blad.strip("; ") else f"zdjęcia ({len(dane)})")
            if not t.get("productMenu"):
                sciezka_menu = "\\".join([PREFIKS_MENU] + [c.strip() for c in w["category"].split(">")])
                odp = api.zapytanie("PUT", "products/products", {"params": {"products": [{
                    "productId": ident, "productMenuItems": [{
                        "productMenuOperation": "add_product", "shopId": SKLEP_ID,
                        "menuId": MENU_ID, "menuItemTextId": sciezka_menu}]}]}})
                blad = "; ".join(bledy_z(r.get("faults")) for r in
                                 ((odp.get("results") or {}).get("productsResults") or []))
                (wpis["bledy"] if blad.strip("; ") else wpis["zrobiono"]).append(
                    f"menu: {blad}" if blad.strip("; ") else "menu")
            kod = w["kod_producenta"].strip()
            if kod and ident not in kody_towarow:
                if kod in zajete:
                    wpis["bledy"].append(f"kod producenta {kod} zajęty przez towar {zajete[kod]}")
                else:
                    odp = api.zapytanie("PUT", "products/sizes", {"mode": "edit", "sizesProductsData": [
                        {"productId": ident, "sizes": [{"sizeId": "uniw",
                                                        "sizeData": {"codeProducer": kod}}]}]})
                    blad = "; ".join(
                        filter(None, [bledy_z(r.get("errors")) for r in odp.get("results") or []] +
                               [bledy_z(s.get("errors")) for r in odp.get("results") or []
                                for s in r.get("sizes") or []]))
                    if blad:
                        wpis["bledy"].append("kod producenta: " + blad)
                    else:
                        wpis["zrobiono"].append("kod producenta")
                        zajete[kod] = ident
        print()

    try:
        with open(sciezka + ".csv", "w", encoding="utf-8-sig", newline="") as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow(["kod_zewnetrzny", "id_idosell", "uzupelniono", "bledy", "dublety"])
            for wpis in wiersze:
                pisarz.writerow([wpis["kod"], wpis["id"], ", ".join(wpis["zrobiono"]),
                                 " | ".join(wpis["bledy"]), ", ".join(map(str, wpis["dublety"]))])
    except OSError as blad:
        print(f"Błąd zapisu dziennika: {blad}")
        return 1

    licznik = Counter(z.split(" (")[0].split(":")[0] for wpis in wiersze for z in wpis["zrobiono"])
    print("Uzupełniono:", dict(licznik))
    print("Towarów z błędami:", sum(1 for wpis in wiersze if wpis["bledy"]))
    print("Dublety:", [(wpis["kod"], wpis["id"], wpis["dublety"]) for wpis in wiersze if wpis["dublety"]])
    print(f"Dziennik: {sciezka}.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
