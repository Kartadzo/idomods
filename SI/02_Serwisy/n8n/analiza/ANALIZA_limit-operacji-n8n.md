# ANALIZA: n8n.idomods.pro – limit operacji, zwiększenie limitu lub optymalizacja automatów

Data: 2026-11-03 · Wstępna analiza (bez zmian w workflowach)
Zadanie: [n8n.idomods.pro - Limit operacji, zwiększenie limitu lub optymalizacja automatów](https://app.clickup.com/t/8696c4dca)
Rodzic: [n8n.idomods.pro - Workflowy, przepływy pracy, automatyzacje](https://app.clickup.com/t/86959gg4f)

---

## 1. Co mówi zadanie (stan faktyczny)

- Zadanie założone **2024-10-25**, opis jest pusty. Cała treść siedzi w komentarzach i załącznikach.
- **Wszystkie komentarze dotyczą Make.com, nie n8n**:
  - automatyczne maile Make „You're reaching your operations limit” dla organizacji BRANDS MANAGO
    (org. 288963, eu1): 28.10.2024, 07.11.2024 (90%), 25.11.2024 (75%), 27.11.2024 (90%);
  - Kuba Lewtak zrobił przekierowanie tych maili do ClickUp (forward Gmail → adres zadania),
    stąd automatyczne komentarze ClickBota „Sprawdź co się stało”;
  - 27.11.2024 Eryk Jakubik: „DOKUPIŁEM OPERACJE W MAKE.COM”. Od tamtej pory brak nowych wpisów.
- Etykieta „Projekt” to nadal `BM: AUTOMATYZACJE (MAKE.COM)`, a tytuł mówi już o `n8n.idomods.pro`.
  Zadanie przeniesiono pod rodzica n8n bez aktualizacji treści.
- Status „w trakcie”, przypisany Dominik Matyjasek, opiekun Kuba Lewtak, estymata 1 h,
  zarejestrowane ~49 min, termin ok. 04.11.2026.

**Wniosek:** nie ma udokumentowanego problemu z limitem w n8n. Jest problem historyczny z Make.com
(rozwiązany zakupem operacji) i tytuł sugerujący, że to samo pytanie trzeba teraz zadać dla n8n.

## 2. Co widać w panelu n8n (odczyt przed wygaśnięciem sesji)

Ekran Overview, konto użytkownika, zakres domyślny (prawdopodobnie ostatnie 7 dni):

| Metryka | Wartość |
|---|---|
| Wykonania produkcyjne | 4 950 (+1,48%) |
| Nieudane wykonania prod. | 9 (+125%) |
| Wskaźnik błędów | 0,2% |
| Średni czas wykonania | 0,45 s |

Workflowy widoczne w projekcie „Personal” (razem 10):

| Workflow | Folder | Stan | Ostatnia zmiana |
|---|---|---|---|
| MT5 Heartbeat IN | MT5 ERYK PRV | Published | 3 tyg. temu |
| Skrypt sprawdzający czy wszystkie aplikacje są aktywne (Chat Google) | ClickUp | Published | 2 mies. |
| ClickUp - SUBTASK (n8n)#2 | ClickUp | Published | 2 mies. |
| Google Ads - SklepWedkarski - Feed ABC | ClickUp | Published | 2 mies. |
| Bot - 'Do Wyceny' | ClickUp | Published | 3 mies. |
| My workflow | PolZoo | – | 3 mies. |
| AppStore w IdoSell - Nowa instalacja | DEV_AppStore | – | 3 mies. |
| [1] Arkusz → komentarz ClickUp (Nowy film SklepWedkarski) | – | Published | 4 mies. |
| ClickUp — Walidacja (createMain + głębokość subtasków) | crm.idomods.pro | – | 4 mies. |
| ClickUp — Eksploracja API (CRM integracja) | crm.idomods.pro | – | 4 mies. |

Instancja ma nowy interfejs (Overview/Insights, Chat, Data tables, „Published”), więc to n8n w wersji
1.11x lub 2.x. Domena własna `n8n.idomods.pro` wskazuje na **self-hosting**
(n8n Cloud działa pod `*.app.n8n.cloud`). To trzeba jeszcze potwierdzić.

## 3. Kluczowa różnica Make vs n8n

- **Make.com** rozlicza **operacje**, czyli każdy moduł w każdym przebiegu. Stąd maile o limicie.
- **n8n self-hosted (Community)** nie ma limitu wykonań ani operacji. Ograniczenia są inne:
  - zasoby serwera (CPU/RAM VPS), tryb `regular` albo `queue` z workerami,
  - rozmiar bazy przez historię wykonań (pruning: `EXECUTIONS_DATA_PRUNE`, `EXECUTIONS_DATA_MAX_AGE`,
    zapisywanie udanych wykonań),
  - limity zewnętrznych API (ClickUp ~100 req/min na token, Google, IdoSell),
  - funkcje płatne (Business/Enterprise: SSO, środowiska, projekty zespołowe), ale nie liczba wykonań.
- **n8n Cloud** ma limit wykonań miesięcznie per plan i tylko wtedy pytanie „zwiększyć limit?” ma sens wprost.

## 4. Hipotezy (do weryfikacji)

1. **H1 – problem dotyczy Make, nie n8n.** Pytanie biznesowe brzmi wtedy „czy migrować scenariusze z Make
   do n8n, żeby nie dokupować operacji?”. To pasowałoby do przeniesienia zadania pod rodzica n8n.
2. **H2 – n8n self-hosted dochodzi do limitu zasobów** (wolne działanie, kolejki, rosnąca baza).
   4 950 wykonań tygodniowo (~700/dzień, ok. 1 co 2 min) to mało dla n8n, ale sprawdzić trzeba,
   co je generuje.
3. **H3 – główne źródło wykonań to workflowy cykliczne/heartbeat**: `MT5 Heartbeat IN`
   i „Skrypt sprawdzający czy wszystkie aplikacje są aktywne”. Optymalizacja polegałaby na
   rzadszym harmonogramie, filtrowaniu na wejściu i niezapisywaniu udanych wykonań.
4. **H4 – widok jest niepełny.** Widzę tylko projekt „Personal” jednego konta. Workflowy innych
   użytkowników (np. Kuby Lewtaka, Katarzyny Woźniak) mogą generować większość ruchu.

## 5. Proponowany zakres analizy właściwej (bez kodu, do akceptacji)

1. Potwierdzić hosting i licencję: Settings → Usage and plan (self-hosted/Cloud, plan, limity).
2. Insights z dłuższego zakresu (30/90 dni) z podziałem na workflow: które generują najwięcej wykonań i błędów.
3. Lista wszystkich workflowów instancji (konto owner/admin), nie tylko „Personal”.
4. Dla 3–5 największych: wyzwalacz (webhook/schedule/polling), częstotliwość, liczba węzłów, ustawienia
   zapisu wykonań. Na tej podstawie lista optymalizacji z szacunkiem zysku.
5. Make.com: stan operacji i lista aktywnych scenariuszy, jeśli H1 jest aktualna,
   jako wejście do decyzji „dokupić / migrować do n8n”.
6. Wynik: raport `analiza/RAPORT_limit-operacji.md` + propozycja odpowiedzi do ClickUp (draft, bez wysyłania).

Odczyt przez interfejs n8n i Claude in Chrome, tylko do odczytu. Opcjonalnie przez `n8n-mcp`
(wciąż niepodpięty, instrukcja: `dokumentacja/01-n8n-mcp-setup.md`) albo Public API z kluczem.

## 6. Założenia

- Analiza jest tylko do odczytu. Nie zmieniam workflowów ani ustawień instancji bez osobnej zgody.
- Dane z Overview dotyczą domyślnego zakresu 7 dni (do potwierdzenia w Insights).
- Wyniki zapisuję w `SI/02_Serwisy/n8n/analiza/`.

## 7. Otwarte pytania

1. **Czego dotyczy zadanie teraz?** Limitu w Make.com (jak w komentarzach), n8n, czy migracji Make → n8n?
2. Czy pojawił się konkretny objaw w n8n (mail o limicie, spowolnienie, zatrzymane workflowy, błąd)? Jeśli tak, kiedy?
3. n8n.idomods.pro: self-hosted (gdzie, jaki VPS) czy n8n Cloud? Kto ma konto owner?
4. Czy mam dostęp do workflowów innych użytkowników, czy analiza ogranicza się do moich?
5. Czy w zakres wchodzi też przegląd scenariuszy Make.com (dostęp do eu1.make.com, org. 288963)?
6. **Sesja n8n wygasła** w trakcie odczytu. Do dalszej pracy potrzebne jest ponowne zalogowanie
   w Chrome (zrób to sam; ja nie wpisuję haseł).
