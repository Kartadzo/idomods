# ivemax.com — pozostałości techniczne na froncie (wersja PL)
Front: `https://shop52797-1.yourtechnicaldomain.com` · przegląd 2026-11-12 (tylko odczyt; koszyk do kroku „Płatność i dostawa”, bez złożenia zamówienia) · zakres: tylko PL

Priorytet: **P1** widoczne dla każdego klienta / psuje SEO · **P2** widoczne na podstronach · **P3** kosmetyka lub do decyzji

| # | Prio | Gdzie (URL) | Co widać (cytat) | Gdzie poprawić w panelu |
|---|---|---|---|---|
| 1 | P1 | `/` – slider główny (`#main_banner1`) | slajd „**Wersje kolorystyczne**” z linkiem do pomocy IdoSell `iai-shop.com/…/samodzielna-zmiana-kolorow-w-standardowym-template-sklepu…`; slajd „Bezproblemowe zwroty” (grafika demo z 2023) | Wygląd sklepu → Bannery / strefy bannerowe (strona główna) |
| 2 | P1 | `/` – sekcja Blog; `/pl/blog.html` | „Pierwszy/Drugi/Trzeci/Czwarty przykładowy wpis na blog” – „To jest krótki opis pierwszego wpisu na blog z kategorii: Pierwsza przykładowa kategoria. **Zmienisz go w dziale MODERACJA > Blog.**” | Moderacja → Blog (usunąć wpisy i kategorię przykładową) |
| 3 | P1 | `/` – sekcja Marki; `/pl/producers.html` | „**Przykładowy producent A**”, „**Przykładowy producent B**” (obok Iveco) | Towary → Producenci (usunąć / ukryć przykładowych) |
| 4 | P1 | stopka – każda strona | kolumna „**Menu 4**” z linkami „Pierwszy … Piąty **przykładowy link**” → `/main.php` | Wygląd sklepu → Menu i podstrony opisowe w masce (menu stopki) |
| 5 | P1 | `/Darmowe-zwroty-Poczta-Polska-cabout-pol-15.html` | „Zasady dotyczące zwrotów – To jest treść strony Zasady dotyczące zwrotów. **Jej zawartość zmienisz w dziale MODERACJA > CMS > Własne podstrony CMS > Strony firmowe.** Możesz tu wpisać dowolnej długości tekst…” | Moderacja → CMS → Własne podstrony → Strony firmowe → „Zasady dotyczące zwrotów” |
| 6 | P1 | karta produktu, np. `/pl/products/2992027-iveco-daily-lozysko-oporowe-sprzegla-2050.html` | **pusty `<title>`**; meta description: „**{product_name}** ➤ Sklep Internetowy Ivemax ☆ …” – zła składnia zmiennej (nie jest podmieniana) | Moderacja → SEO → Domyślne meta (szablon dla kart towarów; zmienne `[iai:…]`) |
| 7 | P2 | `/pl/news.html` | „Drugi/Pierwszy **przykładowy news** – To jest krótki opis… **Zmienisz go w dziale MODERACJA > Aktualności.**” (2017–2018) | Moderacja → Aktualności |
| 8 | P2 | menu kategorii (strona główna) | pozycje „Filtry”, „Części Karoserii”, „silniki i osprzęt”, „wyposażenie wnętrz”, „układ hamulcowy” prowadzą na `/` (puste linki) | Menu kategorii / węzły menu (do decyzji: podpiąć kategorie albo ukryć) |
| 9 | P2 | wersja EN (widoczna dla odwiedzających) | meta description: „**You can change the shop description in MODERATION \ SEO**”, keywords: „You can change the shop keywords in MODERATION \ SEO” | Moderacja → SEO → Domyślne meta (EN) |
| 10 | P2 | wersje DE/FR/IT/ES/NL/SV | meta title i description = `[iai:shop_name]`; wszystkie 8 języków widoczne dla odwiedzających mimo braku tłumaczeń | Administracja → Konfiguracja języków (widoczność) / SEO (meta per język) |
| 11 | P2 | `/pl/terms.html`, `/pl/privacy-and-cookie-notice.html` | e-mail sprzedawcy **`shop@shop52797-1.yourtechnicaldomain.com`** i adres domeny technicznej w treści (regulamin generowany automatycznie) | Administracja → Konta e-mail (konto w domenie ivemax.com) + Regulamin, zgody, polityki |
| 12 | P2 | lista kategorii, np. `/pl/menu/sprzegla-171.html` | tytuł „Sprzęgła \| Części Iveco Daily \| **VIKI-CZĘŚCI**” – nazwa firmy zamiast marki Ivemax | Moderacja → SEO / nazwa sklepu w meta |
| 13 | P2 | koszyk → „Płatność i dostawa” | forma dostawy „**Niestandardowy**”; wszystkie dostawy (także palety) „**Gratis!**” przy koszyku 250 zł | indywidualna aplikacja dostaw w panelu (Apps) + dodatek „Logika Palet - Test” – do weryfikacji, czy to zamierzone |
| 14 | P3 | karta produktu – ramka korzyści | „Darmowa i szybka dostawa”, „Odroczone płatności. Kup teraz, zapłać za 30 dni”, „**Sprawdź, w którym sklepie obejrzysz i kupisz od ręki**” – teksty szablonu, do potwierdzenia, czy zgodne z ofertą (sklepy stacjonarne?) | Wygląd / szablon karty towaru |
| 15 | P3 | COP – płatności | widoczne „**Pobranie**” i PayPo; PayPal i Stripe – brak | Profile płatności (do decyzji klienta) |
| 16 | P3 | koszyk / dodatki | aktywny dodatek JS „**Logika Palet - Test**” (koszyk) – nazwa testowa na produkcji | Wygląd → Dodatki HTML i JavaScript |
| 17 | P3 | stopka | link „Powered by IdoSell” (badge) | Logo „Powered by IdoSell” – opcja White-Label (płatna) |

## Nie znaleziono
- Linków do Shopera / Shoparena (`shoper`, `shoparena`, `sklep407784`) – brak na sprawdzonych stronach.
- Resztek **edrone** w kodzie stron – brak (DNS poza zakresem przeglądu).
- „Lorem ipsum” – brak.

## Sprawdzone strony
`/`, `/pl/terms.html`, `/pl/privacy-and-cookie-notice.html`, `/pl/delivery.html`, `/pl/payments.html`, `/pl/returns-and_replacements.html`, `/pl/contact.html`, `/pl/order-open.html`, `/Darmowe-zwroty-Poczta-Polska-cabout-pol-15.html`, `/pl/blog.html`, `/pl/news.html`, `/pl/producers.html`, `/pl/login.html`, `/pl/client-new.html`, `/pl/basketedit.html`, `/pl/order1.html`, `/pl/newsletter.html`, `/pl/rma-open.html`, `/pl/returns-open.html`, 404, `/robots.txt`, kategoria „Sprzęgła”, karta produktu 2992027.

Nie sprawdzono: maili podglądowych (krok 6), podstron CMS niepodlinkowanych w stopce („Paczkomaty 24/7”, „Karta podarunkowa”, „Pozostałe informacje 1–3”, „Ankiety”) – w panelu istnieją, ich widoczność do sprawdzenia przy porządkach.

Uwaga: w koszyku sesji przeglądarki (DESKTOP-chrome-SI-MD) został 1 szt. produktu 2992027 – zamówienie nie zostało złożone.
