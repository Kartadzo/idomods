"""Import nowych towarów z Shoparena do IdoSell przez REST Admin API.

Dla każdego towaru z nowe_towary_shoparena.csv: POST products/products (ukryty, tylko pol,
zdjęcia z URL), PUT products/products (menu sklepu), PUT products/sizes (kod producenta,
jeśli wolny). Pomija towary, których kod zewnętrzny już jest w sklepie, więc ponowne
uruchomienie nie tworzy duplikatów. Decyzje: ANALIZA_api_nowe_towary.md.

Uruchomienie: run_api_nowe_towary.bat. Najpierw próba na 1 towarze, potem pytanie o resztę.
Skróty: --tylko-proba (bez pytania, kończy po próbie), --bez-pytania (wysyła wszystko).
"""

import csv
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

from api_kod_producenta import KlientApi, PLIK_KONFIGURACJI, FOLDER_WYNIKOW

PLIK_TOWAROW = "nowe_towary_shoparena.csv"
PLIK_SHOPARENA = "shopArena*.csv"
PLIK_IDOSELL = "products_export*.csv"

SKLEP_ID = 1
MENU_ID = 1
KATEGORIA_TYMCZASOWA = "*Kategoria tymczasowa"
PREFIKS_MENU = "Kategorie"
ROZMIAR_PACZKI = 20
ROZMIAR_STRONY = 100

STATUS_UTWORZONO = "utworzono"
STATUS_UTWORZONO_UWAGI = "utworzono z uwagami"
STATUS_BLAD = "błąd"
STATUS_JEST = "pominięto - kod zewnętrzny już w sklepie"


def najnowszy(wzorzec: str) -> str:
    """Zwraca najnowszy plik pasujący do wzorca albo zgłasza błąd."""
    pliki = sorted(glob.glob(wzorzec), key=os.path.getmtime, reverse=True)
    if not pliki:
        raise FileNotFoundError(f"brak pliku {wzorzec}")
    return pliki[0]


def mapy_z_eksportu() -> Tuple[Dict[str, int], int, Dict[str, int]]:
    """Zwraca (kategoria Shoparena -> categoryId, ID kategorii tymczasowej, producent -> ID).

    Kategorię Shoparena przypisuje wg przeniesionych towarów (most kod zewnętrzny ->
    product_code), z pominięciem kategorii tymczasowej; wygrywa najczęstsza.
    """
    csv.field_size_limit(2**31 - 1)
    kategorie_sa = {}
    with open(najnowszy(PLIK_SHOPARENA), encoding="utf-8-sig", newline="") as plik:
        for w in csv.DictReader(plik):
            kategorie_sa[w["product_code"].strip()] = w["category"]
    glosy = defaultdict(Counter)
    tymczasowa = 0
    producenci = {}
    with open(najnowszy(PLIK_IDOSELL), encoding="utf-8-sig", newline="") as plik:
        for w in csv.DictReader(plik):
            producenci[w["/producer@name"]] = int(w["/producer@id"] or 0)
            if w["/category@name[pol]"] == KATEGORIA_TYMCZASOWA:
                tymczasowa = int(w["/category@id"])
                continue
            kod = w["/sizes/size@code_external"].strip()
            kod = kod[4:] if kod.startswith("KZS-") else kod
            if kod in kategorie_sa:
                glosy[kategorie_sa[kod]][int(w["/category@id"])] += 1
    mapa = {kat: licznik.most_common(1)[0][0] for kat, licznik in glosy.items()}
    return mapa, tymczasowa, producenci


def stan_sklepu(api: KlientApi) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Zwraca (kod zewnętrzny -> productId, kod producenta -> productId) ze stanu na żywo."""
    zewnetrzne, producenta = {}, {}
    strona = 0
    while True:
        odp = api.zapytanie(
            "GET", f"products/sizes?result::page={strona}&result::pageNumber={ROZMIAR_STRONY}"
        )
        wyniki = odp.get("results") or {}
        for towar in (wyniki.values() if isinstance(wyniki, dict) else wyniki):
            for r in towar.get("sizesResult", []):
                if (r.get("productSizeCodeExternal") or "").strip():
                    zewnetrzne[r["productSizeCodeExternal"].strip()] = int(towar["productId"])
                if (r.get("productProducerCode") or "").strip():
                    producenta[r["productProducerCode"].strip()] = int(towar["productId"])
        stron = int((odp.get("result") or {}).get("pageAll", 0))
        strona += 1
        print(f"\r  odczyt stanu: strona {strona}/{stron}", end="")
        if strona >= stron:
            print()
            return zewnetrzne, producenta


def jezyk(pole: str, klucz: str, wartosc: str) -> dict:
    """Buduje obiekt językowy API dla polskiej wersji."""
    return {pole: [{"langId": "pol", klucz: wartosc}]}


def towar_api(w: dict, kategoria_id: int, producent_id: int) -> dict:
    """Mapuje wiersz listy nowych towarów na obiekt products[] bramki POST."""
    zdjecia = [w[f"images {i}"] for i in range(1, 10) if w.get(f"images {i}", "").strip()]
    towar = {
        "productSizeCodeExternal": w["kod_zewnetrzny"],
        "categoryId": kategoria_id,
        "sizesGroupId": -1,
        "unitId": 0,
        "productVat": 23,
        "productVatFree": "n",
        "productRetailPrice": float(w["price"]),
        "productInVisible": "n",
        "productInPersistent": "y",
        "productInExportToPriceComparisonSites": "y",
        "availableProfile": 1,
        "shopsMask": 1,
        "productPictures": zdjecia,
        "productNames": jezyk("productNamesLangData", "productName", w["name"].strip()),
        "productDescriptions": jezyk(
            "productDescriptionsLangData", "productDescription", w["short_description"].strip()),
        "productLongDescriptions": jezyk(
            "productLongDescriptionsLangData", "productLongDescription", w["description"]),
    }
    if producent_id:
        towar["producerId"] = producent_id
    for kolumna, pole, klucz in (
        ("seo_title", "productMetaTitlesLangData", "productMetaTitle"),
        ("seo_description", "productMetaDescriptionsLangData", "productMetaDescription"),
        ("seo_keywords", "productMetaKeywordsLangData", "productMetaKeyword"),
    ):
        if w.get(kolumna, "").strip():
            obiekt = pole.replace("LangData", "")
            towar[obiekt] = jezyk(pole, klucz, w[kolumna].strip())
    return towar


def bledy_z(lista) -> str:
    """Skleja komunikaty błędów API (faults/errors) w jeden tekst."""
    teksty = []
    for b in lista or []:
        if isinstance(b, dict) and (b.get("faultCode") not in (None, 0, "0") or b.get("faultString")):
            teksty.append(f"{b.get('faultCode')}: {b.get('faultString', '')}".strip())
    return "; ".join(teksty)


def przetworz(api: KlientApi, paczka: List[dict], mapy, zajete_kody: Dict[str, int]) -> None:
    """Tworzy paczkę towarów, przypina menu i wpisuje kody producenta; ustawia statusy."""
    mapa_kat, tymczasowa, producenci = mapy
    for p in paczka:
        p["kategoria_id"] = mapa_kat.get(p["w"]["category"], tymczasowa)
    dane = {
        "settings": {"settingAddingCategoryAllowed": "n", "settingAddingProducerAllowed": "n",
                     "settingAddingSizeAllowed": "n"},
        "picturesSettings": {"picturesSettingInputType": "url",
                             "picturesSettingOverwrite": "n", "picturesSettingScaling": "y"},
        "products": [towar_api(p["w"], p["kategoria_id"], producenci.get(p["w"]["producer"], 0))
                     for p in paczka],
    }
    odp = api.zapytanie("POST", "products/products", {"params": dane})
    wyniki = ((odp.get("results") or {}).get("productsResults")) or []
    po_kodzie = {str(r.get("productSizeCodeExternal") or ""): r for r in wyniki}
    for nr, p in enumerate(paczka):
        r = po_kodzie.get(p["w"]["kod_zewnetrzny"]) or (wyniki[nr] if nr < len(wyniki) else {})
        p["id"] = int(r.get("productId") or 0)
        blad = bledy_z(r.get("faults")) or ("" if p["id"] else json.dumps(odp, ensure_ascii=False)[:300])
        p["status"] = STATUS_BLAD if not p["id"] else STATUS_UTWORZONO
        p["uwagi"] = [blad] if blad else []

    utworzone = [p for p in paczka if p["id"]]
    if not utworzone:
        return
    menu = {"products": [
        {"productId": p["id"], "productMenuItems": [{
            "productMenuOperation": "add_product", "shopId": SKLEP_ID, "menuId": MENU_ID,
            "menuItemTextId": "\\".join(
                [PREFIKS_MENU] + [c.strip() for c in p["w"]["category"].split(">")]),
        }]} for p in utworzone]}
    odp = api.zapytanie("PUT", "products/products", {"params": menu})
    for r in ((odp.get("results") or {}).get("productsResults")) or []:
        blad = bledy_z(r.get("faults"))
        if blad:
            for p in utworzone:
                if p["id"] == int(r.get("productId") or 0):
                    p["uwagi"].append("menu: " + blad)

    kody = []
    for p in utworzone:
        kod = p["w"]["kod_producenta"].strip()
        if not kod:
            continue
        if kod in zajete_kody:
            p["uwagi"].append(f"kod producenta {kod} zajęty przez towar {zajete_kody[kod]} - pominięty")
            continue
        zajete_kody[kod] = p["id"]
        kody.append(p)
    if kody:
        odp = api.zapytanie("PUT", "products/sizes", {"mode": "edit", "sizesProductsData": [
            {"productId": p["id"], "sizes": [{"sizeId": "uniw",
                                              "sizeData": {"codeProducer": p["w"]["kod_producenta"]}}]}
            for p in kody]})
        for r in odp.get("results") or []:
            teksty = bledy_z(r.get("errors"))
            for rozmiar in r.get("sizes") or []:
                teksty = "; ".join(filter(None, [teksty, bledy_z(rozmiar.get("errors"))]))
            if teksty:
                for p in kody:
                    if p["id"] == int(r.get("productId") or 0):
                        p["uwagi"].append("kod producenta: " + teksty)
    for p in utworzone:
        if p["uwagi"]:
            p["status"] = STATUS_UTWORZONO_UWAGI
        if p["w"]["uwagi"]:
            p["uwagi"].append(p["w"]["uwagi"])


def main() -> int:
    """Planuje import, wykonuje próbę na 1 towarze, pyta o resztę i zapisuje dziennik."""
    tylko_proba = "--tylko-proba" in sys.argv
    bez_pytania = "--bez-pytania" in sys.argv
    try:
        with open(PLIK_KONFIGURACJI, encoding="utf-8") as plik:
            konf = json.load(plik)
        with open(PLIK_TOWAROW, encoding="utf-8-sig", newline="") as plik:
            towary = list(csv.DictReader(plik))
        mapy = mapy_z_eksportu()
    except (OSError, ValueError, KeyError) as blad:
        print(f"Błąd odczytu danych wejściowych: {blad}")
        return 1
    os.makedirs(FOLDER_WYNIKOW, exist_ok=True)
    sciezka = os.path.join(FOLDER_WYNIKOW,
                           f"api_nowe_towary_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}")

    pozycje = [{"w": w, "id": 0, "uwagi": []} for w in towary]
    with open(sciezka + ".jsonl", "w", encoding="utf-8") as dziennik:
        api = KlientApi(konf["domena"], konf["klucz_api"], dziennik)
        print("Odczyt stanu sklepu…")
        zewnetrzne, zajete_kody = stan_sklepu(api)
        do_wyslania = []
        for p in pozycje:
            kod = p["w"]["kod_zewnetrzny"]
            if kod in zewnetrzne:
                p["id"], p["status"] = zewnetrzne[kod], STATUS_JEST
            else:
                do_wyslania.append(p)
        print(f"Do utworzenia: {len(do_wyslania)}, już w sklepie: {len(pozycje) - len(do_wyslania)}")

        if do_wyslania:
            proba, reszta = do_wyslania[:1], do_wyslania[1:]
            przetworz(api, proba, mapy, zajete_kody)
            for p in proba:
                print(f"\nPróba: {p['w']['product_code']} → towar {p['id']} ({p['status']})")
                for u in p["uwagi"]:
                    print("  ", u)
            udana = all(p["id"] for p in proba)
            if not udana:
                print("Próba nieudana — przerywam.")
            elif reszta and not tylko_proba and (bez_pytania or input(
                    f"\nObejrzyj towar w panelu. Utworzyć pozostałe {len(reszta)}? [t/N]: "
            ).strip().lower() == "t"):
                for start in range(0, len(reszta), ROZMIAR_PACZKI):
                    przetworz(api, reszta[start:start + ROZMIAR_PACZKI], mapy, zajete_kody)
                    print(f"\r  przetworzono {min(start + ROZMIAR_PACZKI, len(reszta))}/{len(reszta)}",
                          end="")
                print()
            for p in reszta:
                p.setdefault("status", "nie wysłano")

    try:
        with open(sciezka + ".csv", "w", encoding="utf-8-sig", newline="") as plik:
            pisarz = csv.writer(plik)
            pisarz.writerow(["product_code", "kod_zewnetrzny", "id_idosell", "nazwa", "kategoria_id",
                             "status", "uwagi"])
            for p in pozycje:
                pisarz.writerow([p["w"]["product_code"], p["w"]["kod_zewnetrzny"], p["id"] or "",
                                 p["w"]["name"].strip(), p.get("kategoria_id", ""), p["status"],
                                 " | ".join(p["uwagi"])])
    except OSError as blad:
        print(f"Błąd zapisu dziennika: {blad}")
        return 1

    print("\nPodsumowanie:")
    for status, liczba in Counter(p["status"] for p in pozycje).most_common():
        print(f"  {status}: {liczba}")
    print(f"\nDziennik: {sciezka}.csv (+ .jsonl z odpowiedziami API)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
