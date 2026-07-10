# AI Instrukcje - Przewodnik

Folder zawiera strukturyzowane instrukcje i założenia dla AI dotyczące kodu w projekcie Domino.

## 📋 Struktura

Każdy język/technologia ma własny podfolder zawierający 2 pliki:

### `assumptions.md`
- Podstawowe założenia o projekcie
- Konwencje i standardy
- Charakterystyka zastosowania
- Najczęściej używane biblioteki
- Typy zadań
- Assumptions dotyczące danych

### `instructions.md`
- Szczegółowe instrukcje implementacji
- Szablony kodu
- Best practices
- Bezpieczeństwo i performance
- Wskazówki stylowe
- Debugging i testowanie

---

## 🐍 Python

**Zastosowanie:** Transformacja danych, ETL, skrypty serverowe

- [Założenia](Python/assumptions.md)
- [Instrukcje](Python/instructions.md)

### Typowe zadania:
- Przetwarzanie CSV/XML
- Migracja baz danych
- Transformacja e-commerce danych
- Raporty i analiza

---

## 🟨 JavaScript

**Zastosowanie:** Front-end, DOM manipulation, tracking

- [Założenia](JavaScript/assumptions.md)
- [Instrukcje](JavaScript/instructions.md)

### Typowe zadania:
- Modyfikacja stron HTML
- Google Tag Manager integration
- Facebook Pixel tracking
- Zarządzanie cookies
- Automatyzacja

---

## 📊 SQL

**Zastosowanie:** Zapytania baz danych, raporty

- [Założenia](SQL/assumptions.md)
- [Instrukcje](SQL/instructions.md)

### Typowe zadania:
- SELECT na danych katalogowych
- Agregacje i raporty
- Eksporty dla narzędzi marketingowych
- Migracje danych
- Analiza PrestaShop

---

## 🔄 XSLT

**Zastosowanie:** Transformacja XML feeds

- [Założenia](XSLT/assumptions.md)
- [Instrukcje](XSLT/instructions.md)

### Typowe zadania:
- Google Shopping feed transformacja
- Multi-language override
- Mapowanie kategorii
- Normalizacja danych XML
- Pinterest/custom feed generation

---

## 🐘 PHP

**Zastosowanie:** Backend skrypty, API, integracje

- [Założenia](PHP/assumptions.md)
- [Instrukcje](PHP/instructions.md)

### Typowe zadania:
- Database operations
- HTTP API calls
- File processing
- PrestaShop integration
- Session management

---

## 🎯 Jak Używać

### Dla AI/Copilota:
Wczytaj odpowiedni plik instructions.md dla języka, w którym pracujesz:

```
# Na podstawie pliku ~/AI_Instrukcje/Python/instructions.md
# Pisz kod Pythona zgodnie z zawartymi wskazówkami
```

### Dla człowieka:
1. Wybierz język/technologię
2. Przeczytaj `assumptions.md` aby zrozumieć kontekst
3. Użyj `instructions.md` jako reference do wzorów kodu

---

## 📝 Konwencje Ogólne

### Encoding
- Zawsze UTF-8
- Polskie znaki (ą, ć, ę, ł, ń, ó, ś, ź, ż) must be supported

### Git
- Ignoruj dane tymczasowe
- Commituj kod z opisem
- Version history important

### Dokumentacja
- Inline comments dla logiki
- Docstrings/JSDoc dla funkcji
- README dla nowych folderów

### Security
- Sanitize wszystkie inputs
- Escape outputs
- Prepared statements dla SQL
- No hardcoded credentials

---

## 🔧 Szybka Referencja

| Język | Version | Encoding | Tab | Style |
|-------|---------|----------|-----|-------|
| Python | 3.8+ | UTF-8 | 4sp | PEP 8 |
| JavaScript | ES6+ | UTF-8 | 2sp | camelCase |
| SQL | MySQL | utf8mb4 | - | UPPER_CASE |
| XSLT | 1.0/2.0 | UTF-8 | 2sp | element-case |
| PHP | 7.2+ | UTF-8 | 4sp | PSR-12 |

---

## 📌 Last Updated
2024-12-10

**Instrukcje stworzone dla projektu Domino E-commerce**
