# -*- coding: utf-8 -*-
"""Gotowiec ICF: kampania dodatków IdoSell z pikselem ChatGPT Ads (OpenAI oaiq).

Czyta dodatki z ../dodatki/0*.html (wersja wdrożona na butyolivier.pl), zamienia
wartości specyficzne dla sklepu na zmienne kampanii [config:…] i zapisuje
piksel_chatgpt_ads.xml do importu w panelu: Dodatki HTML i JavaScript → Import ICF kampanii.

Uruchomienie: python zbuduj_icf.py [kod_języka]
  bez argumentu → piksel_chatgpt_ads.xml (pol); z kodem, np. gre → piksel_chatgpt_ads_gre.xml.
  Język, do którego trafia treść dodatków, wyznacza WYŁĄCZNIE <language name="…"/> w pliku —
  wybór języka w oknie importu panelu niczego nie zmienia (sprawdzone 2026-11-10, abczoo.gr).
"""
import os
import re
import sys
import time
from xml.sax.saxutils import escape, quoteattr

TU = os.path.dirname(os.path.abspath(__file__))
DODATKI = os.path.join(TU, '..', 'dodatki')
WYJSCIE = os.path.join(TU, 'piksel_chatgpt_ads.xml')
WERSJA = '1.0'

# Zmienne kampanii (pola w edycji kampanii po imporcie).
USTAWIENIA = [
    ('pixel_id', 'Pixel ID ChatGPT Ads (OpenAI) - Ads Manager, Events Manager', ''),
    ('currency', 'Waluta sklepu, kod ISO 4217 (np. PLN, EUR, CZK)', 'PLN'),
]

# plik, tytuł dodatku, region, strony, wyświetlanie dynamiczne
DODATKI_KAMPANII = [
    ('01_chatgpt_init.html', '[ChatGPT Ads] init', 'head', 'all', 'no'),
    ('02_consent.html', '[ChatGPT Ads] consent - wymaga zgody na cookies reklamowe', 'head', 'all', 'yes'),
    ('03_page_viewed.html', '[ChatGPT Ads] page_viewed', 'body_bottom', 'all', 'yes'),
    ('04_contents_viewed.html', '[ChatGPT Ads] contents_viewed', 'body_bottom', 'projector;', 'yes'),
    ('05_items_added.html', '[ChatGPT Ads] items_added', 'body_bottom', 'projector;', 'yes'),
    ('06_checkout_started.html', '[ChatGPT Ads] checkout_started', 'body_bottom', 'order1;', 'yes'),
    ('07_order_created.html', '[ChatGPT Ads] order_created', 'body_bottom', 'after_order;payment_success;', 'yes'),
]


def podmien(tekst, stare, nowe, plik, ile=None):
    """Podmiana z kontrolą: brak trafienia = zmienił się dodatek źródłowy, trzeba poprawić builder."""
    n = tekst.count(stare)
    if n == 0 or (ile is not None and n != ile):
        sys.exit(f'BŁĄD: {plik}: oczekiwano {ile or "≥1"} wystąpień {stare!r}, jest {n}')
    return tekst.replace(stare, nowe)


def uogolnij(plik, kod):
    if plik == '01_chatgpt_init.html':
        kod = podmien(kod, "  window.oaiqSafe = function () {",
                      "  // Waluta ze zmiennej kampanii „currency” (domyślnie PLN).\n"
                      "  window.oaiqCurrency = (function (c) {\n"
                      "    c = String(c || '').trim().toUpperCase();\n"
                      "    return /^[A-Z]{3}$/.test(c) ? c : 'PLN';\n"
                      "  })('[config:currency]');\n\n"
                      "  window.oaiqSafe = function () {", plik, 1)
    elif plik == '02_consent.html':
        kod = re.sub(r"pixelId: '[^']*'", "pixelId: pixelId", kod)
        kod = podmien(kod, "    if (window.oaiq && !window.oaiqConsentGranted) {",
                      "    // Pixel ID ze zmiennej kampanii „pixel_id”. Pusty → SDK się nie ładuje.\n"
                      "    const pixelId = String('[config:pixel_id]').trim();\n"
                      "    if (window.oaiq && !window.oaiqConsentGranted && /^[A-Za-z0-9_-]{8,}$/.test(pixelId)) {",
                      plik, 1)
        # oppref ze strony wejścia: IdoSell wstawia „consent” dopiero na stronie po kliknięciu zgody,
        # a SDK czyta oppref tylko z bieżącego adresu. Bez zapisu przed zgodą — odczyt z document.referrer.
        # SDK przyjmuje init.oppref tylko po udzielonej zgodzie, stąd drugie init po consent true.
        kod = podmien(kod, "      oaiq('consent', true);\n",
                      "      oaiq('consent', true);\n\n"
                      "      // ID kliknięcia reklamy ze strony wejścia: zgodę kliknięto na stronie z ?oppref=,\n"
                      "      // a ten dodatek IdoSell wstawia dopiero na następnej stronie (bez oppref w adresie).\n"
                      "      try {\n"
                      "        const hasUrlOppref = new URLSearchParams(location.search).has('oppref');\n"
                      "        const hasCookieOppref = /(?:^|;\\s*)__oppref=/.test(document.cookie);\n"
                      "        if (!hasUrlOppref && !hasCookieOppref && document.referrer) {\n"
                      "          const ref = new URL(document.referrer);\n"
                      "          const landingOppref = ref.host === location.host ? (ref.searchParams.get('oppref') || '').trim() : '';\n"
                      "          if (landingOppref) {\n"
                      "            oaiq('init', { oppref: landingOppref });\n"
                      "          }\n"
                      "        }\n"
                      "      } catch (e) {}\n", plik, 1)
    elif plik == '07_order_created.html':
        # Koszt dostawy pomijamy: kwota = wartość towarów. Ceny towarów skalowane do tej wartości,
        # bo na stronie po zamówieniu [iai:product_price_gross_float] potrafi zwrócić wartość zamówienia
        # (abczoo.gr 2026-11-10: 13,91 zamiast 8,01). Przy poprawnych cenach współczynnik = 1.
        kod = podmien(kod,
                      "    oaiqSafe('measure', 'order_created', {\n"
                      "      type: 'contents',\n"
                      "      amount: oaiqAmount('[iai:order_worth_cpa2]'),\n"
                      "      currency: 'PLN',\n"
                      "      contents: oaiqItems('#oaiq-order-items')\n"
                      "    }, {",
                      "    // Wartość towarów bez kosztu dostawy.\n"
                      "    const contents = oaiqItems('#oaiq-order-items');\n"
                      "    const itemsSum = contents.reduce(function (sum, item) {\n"
                      "      return sum + item.amount * item.quantity;\n"
                      "    }, 0);\n"
                      "    const productsAmount = oaiqAmount('[iai:products_worth_cpa2]') || itemsSum;\n"
                      "    if (productsAmount > 0 && itemsSum > 0 && itemsSum !== productsAmount) {\n"
                      "      const ratio = productsAmount / itemsSum;\n"
                      "      contents.forEach(function (item) {\n"
                      "        item.amount = Math.round(item.amount * ratio);\n"
                      "      });\n"
                      "    }\n\n"
                      "    oaiqSafe('measure', 'order_created', {\n"
                      "      type: 'contents',\n"
                      "      amount: productsAmount,\n"
                      "      currency: 'PLN',\n"
                      "      contents: contents\n"
                      "    }, {", plik, 1)
    kod = kod.replace("currency: 'PLN'", "currency: window.oaiqCurrency || 'PLN'")
    for zakazane in (r"currency: 'PLN'", r"pixelId: '", 'HxtQ'):
        if zakazane in kod:
            sys.exit(f'BŁĄD: {plik}: zostało {zakazane!r} (wartość sklepu źródłowego)')
    return kod


def dodatek_xml(tytul, kod, region, strony, dynamicznie):
    pola = [
        ('title', escape(tytul)),
        ('text_main_0', '<![CDATA[' + kod + ']]>'),
        ('active', 'normal_mobile'),
        ('format', 'html'),
        ('region', region),
        ('client_type', 'all'),
        ('clients_with_rebate_code', 'all'),
        ('clients_subscribed', 'all'),
        ('clients_with_orders', 'all'),
        ('auto_block', 'n'),
        ('site', strony),
        ('timeout', '1'),
        ('display_dynamically', dynamicznie),
        ('snippet_activated', 'yes'),
        ('only_support', 'no'),
    ]
    return '<contents>' + ''.join(f'<content type="{k}">{v}</content>' for k, v in pola) + '</contents>'


def main():
    jezyk = (sys.argv[1] if len(sys.argv) > 1 else 'pol').strip().lower()
    if not re.fullmatch(r'[a-z]{3}', jezyk):
        sys.exit(f'BŁĄD: kod języka IdoSell to 3 litery (pol, eng, gre…), podano {jezyk!r}')
    wyjscie = WYJSCIE if jezyk == 'pol' else WYJSCIE.replace('.xml', f'_{jezyk}.xml')
    opis = (
        'Autor: IdoMods.pl\n'
        'Support: kontakt@idomods.pl\n'
        f'Version: {WERSJA}\n'
        '-----------------------------------------\n'
        'Piksel ChatGPT Ads (OpenAI oaiq): page_viewed, contents_viewed, items_added, checkout_started, order_created.\n'
        'Po imporcie: 1) w edycji kampanii wpisz Pixel ID; 2) w dodatku "consent" dodaj plik cookie: dostawca ChatGPT, kategoria reklamowe.\n'
        + time.strftime(' %Y.%m.%d %H:%M:%S')
    )
    ustawienia = ''.join(
        f'<setting type="config" name="{n}" description={quoteattr(d)} value={quoteattr(v)} />'
        for n, d, v in USTAWIENIA)
    czesci = []
    for plik, tytul, region, strony, dyn in DODATKI_KAMPANII:
        with open(os.path.join(DODATKI, plik), encoding='utf-8') as f:
            kod = uogolnij(plik, f.read().strip())
        if ']]>' in kod:
            sys.exit(f'BŁĄD: {plik}: ]]> w kodzie')
        czesci.append(dodatek_xml(tytul, kod, region, strony, dyn))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<repository file_format="ICF" version="1.0"><element id="{int(time.time())}">\n'
        f'<meta><title>[IdoMods.pl] ChatGPT Ads - piksel OpenAI</title><description>{escape(opis)}</description>'
        f'<icon encoding="base64"></icon><language name="{jezyk}"/></meta>\n'
        '<classification><type name="snippets_campaign"/></classification>\n'
        f'<settings>{ustawienia}</settings>\n'
        + '\n'.join(czesci) +
        '\n<enclosures> </enclosures>\n</element>\n</repository>\n'
    )
    with open(wyjscie, 'w', encoding='utf-8', newline='\n') as f:
        f.write(xml)
    print('OK', wyjscie, len(DODATKI_KAMPANII), 'dodatków, język', jezyk)


if __name__ == '__main__':
    main()
