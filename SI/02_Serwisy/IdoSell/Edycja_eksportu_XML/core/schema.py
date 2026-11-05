# -*- coding: utf-8 -*-
"""Rejestr pól - jedyne miejsce, które wie, gdzie w rekordzie leży dana wartość.

Rdzeń jest pisany ręcznie, żeby pola miały polskie etykiety i sensowne grupy.
Reszta - parametry z panelu i kolumny spoza rdzenia - dokłada się po skanie
pliku, więc nic nie ginie po cichu.

Pole opisuje wartość w obu źródłach naraz. `sources` mówi, w którym pliku
w ogóle występuje: pole nieobecne w wybranym źródle zostaje na liście, tylko
wyszarzone, żeby użytkownik widział pełen zakres możliwości.
"""

BOTH = ("xml", "csv")
XML_ONLY = ("xml",)
CSV_ONLY = ("csv",)

# Rodzaje pól - decydują, jak sięgnąć po wartość.
KIND_VALUE = "value"      # values[path]
KIND_LANG = "lang"        # values[path + '[lang]'] z odwrotem do path
KIND_BLOCK = "block"      # blocks[element][@attr], wybór po sklepie i rozmiarze
KIND_SIZE = "size"        # klucz w słowniku rozmiaru
KIND_IMAGES = "images"    # kolekcja adresów, rozbijana przez expander
KIND_PARAMS = "params"    # parametry, rozbijane przez expander


class Context(object):
    """Wybory użytkownika wpływające na odczyt: język, sklep, bieżący rozmiar."""

    __slots__ = ("lang", "site", "size")

    def __init__(self, lang=u"pol", site=u"1", size=None):
        self.lang = lang
        self.site = site
        self.size = size


class Field(object):

    __slots__ = ("id", "label", "group", "kind", "path", "element", "attr",
                 "alt_path", "alt_element", "sources", "type", "multi",
                 "image_kind", "dynamic", "note")

    def __init__(self, id, label, group, kind=KIND_VALUE, path=None, element=None,
                 attr=None, sources=BOTH, type="text", multi=False,
                 image_kind=None, dynamic=False, note=u"", alt_path=None,
                 alt_element=None):
        self.id = id
        self.label = label
        self.group = group
        self.kind = kind
        self.path = path
        self.element = element
        self.attr = attr
        # Ta sama wartość bywa zapisana inaczej w każdym z formatów:
        # CSV ma `/iai_category@path`, XML `/category_idosell@path`. Druga
        # ścieżka jest odwrotem - sprawdzana, gdy pierwsza nic nie zwróci.
        self.alt_path = alt_path
        self.alt_element = alt_element
        self.sources = sources
        self.type = type
        self.multi = multi
        self.image_kind = image_kind
        self.dynamic = dynamic
        self.note = note

    def available_in(self, source_type):
        return source_type in self.sources

    def resolve(self, record, ctx):
        """Wartość pola dla danego rekordu i kontekstu. Zawsze tekst albo lista."""
        kind = self.kind
        if kind == KIND_VALUE:
            for path in self._paths():
                # Najpierw wersja w wybranym języku - inaczej lista tłumaczeń
                # oddawałaby pierwszy język z dokumentu zamiast wybranego.
                # W CSV atrybuty tekstowe noszą ten sufiks zawsze: '@path[pol]'.
                value = record.first(u"%s[%s]" % (path, ctx.lang))
                if value:
                    return value
                value = record.first(path)
                if value:
                    return value
            return u""
        if kind == KIND_LANG:
            for path in self._paths():
                value = record.first(u"%s[%s]" % (path, ctx.lang))
                if not value:
                    value = record.first(path)
                if value:
                    return value
            return u""
        if kind == KIND_BLOCK:
            size_id = ctx.size.get(u"@id") if ctx.size else None
            for element in self._elements():
                entry = record.block(element, site=ctx.site, size_id=size_id)
                if entry is not None:
                    value = _pick_attr(entry, self.attr, ctx.lang)
                    if value:
                        return value
                    continue
                value = _with_lang(record.values, element + self.attr, ctx.lang,
                                   getter=record.first)
                if value:
                    return value
            return u"" 
        if kind == KIND_SIZE:
            if not ctx.size:
                return u""
            for path in self._paths():
                value = record.size_value(ctx.size, path)
                if not value:
                    value = _pick_attr(ctx.size, path, ctx.lang)
                if value:
                    return value
            return u""
        if kind == KIND_IMAGES:
            return list(record.images.get(self.image_kind) or [])
        return u""

    def _paths(self):
        return _as_list(self.path) + _as_list(self.alt_path)

    def _elements(self):
        return _as_list(self.element) + _as_list(self.alt_element)

    def __repr__(self):
        return "<Field %s>" % self.id


def _as_list(value):
    """Ścieżka bywa jedna albo kilka - obie postaci mają działać tak samo."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [item for item in value if item]
    return [value]


def _pick_attr(mapping, attr, lang):
    """Atrybut z uwzględnieniem sufiksu języka, jaki nosi CSV.

    Panel zapisuje `/category@name[pol]`, a XML `name` z `xml:lang`. Pole
    deklaruje `@name`, więc szukamy najpierw wprost, potem w wybranym języku,
    a na końcu w dowolnym - lepiej pokazać wartość obcojęzyczną niż pustkę.
    """
    value = mapping.get(attr)
    if value:
        return value
    value = mapping.get(u"%s[%s]" % (attr, lang))
    if value:
        return value
    prefix = attr + u"["
    for key in sorted(mapping):
        if key.startswith(prefix) and mapping[key]:
            return mapping[key]
    return u""


def _with_lang(values, path, lang, getter):
    value = getter(path)
    if value:
        return value
    return getter(u"%s[%s]" % (path, lang))


def _f(*args, **kwargs):
    return Field(*args, **kwargs)


# ---------------------------------------------------------------------------
# Rdzeń rejestru
# ---------------------------------------------------------------------------

G_BASIC = u"Podstawowe"
G_DESC = u"Opis"
G_PRICE = u"Ceny"
G_SIZE = u"Rozmiary"
G_STOCK = u"Dostępność"
G_IMAGE = u"Zdjęcia"
G_PARAM = u"Parametry"
G_DATE = u"Daty"
G_OPINION = u"Opinie"
G_ENTITY = u"Podmiot odpowiedzialny"
G_OTHER = u"Nierozpoznane"

#: Grupy pominięte na liście pól - mają własne sekcje z pełną konfiguracją,
#: więc pokazywanie ich jeszcze raz jako zwykłych kolumn tylko myli.
HIDDEN_GROUPS = (G_IMAGE, G_PARAM)

CORE_FIELDS = [
    # -- podstawowe --------------------------------------------------------
    _f("product_id", u"ID produktu", G_BASIC, KIND_VALUE, path=u"@id"),
    _f("code_on_card", u"Kod na karcie (EAN)", G_BASIC, KIND_VALUE, path=u"@code_on_card"),
    _f("code_producer", u"Kod producenta", G_BASIC, KIND_VALUE, path=u"@code_producer",
       sources=CSV_ONLY, note=u"w XML tylko na rozmiarze"),
    _f("currency", u"Waluta", G_BASIC, KIND_VALUE, path=u"@currency"),
    _f("vat", u"Stawka VAT", G_BASIC, KIND_VALUE, path=u"@vat", type="number"),
    _f("product_type", u"Typ produktu", G_BASIC, KIND_VALUE, path=u"@type"),
    _f("country_of_origin", u"Kraj pochodzenia", G_BASIC, KIND_VALUE,
       path=u"@country_of_origin"),
    _f("producer_id", u"ID producenta", G_BASIC, KIND_BLOCK, element=u"/producer", attr=u"@id"),
    _f("producer_name", u"Producent", G_BASIC, KIND_BLOCK, element=u"/producer", attr=u"@name"),
    _f("category_id", u"ID kategorii", G_BASIC, KIND_BLOCK, element=u"/category", attr=u"@id"),
    _f("category_name", u"Kategoria", G_BASIC, KIND_BLOCK, element=u"/category", attr=u"@name"),
    _f("idosell_category_id", u"ID kategorii IdoSell", G_BASIC, KIND_BLOCK,
       element=u"/iai_category", attr=u"@id", alt_element=u"/category_idosell"),
    _f("idosell_category_path", u"Ścieżka kategorii IdoSell", G_BASIC, KIND_VALUE,
       path=u"/iai_category@path",
       alt_path=[u"/category_idosell@path", u"/category_idosell_translation@path"],
       note=u"gdy pusta w języku sklepu, bierze tłumaczenie"),
    _f("series_id", u"ID serii", G_BASIC, KIND_BLOCK, element=u"/series", attr=u"@id"),
    _f("series_name", u"Seria", G_BASIC, KIND_BLOCK, element=u"/series", attr=u"@name"),
    _f("unit_name", u"Jednostka", G_BASIC, KIND_BLOCK, element=u"/unit", attr=u"@name"),
    _f("card_url", u"Adres karty produktu", G_BASIC, KIND_BLOCK, element=u"/card", attr=u"@url"),
    _f("deliverer_id", u"ID dostawcy", G_BASIC, KIND_BLOCK, element=u"/deliverer", attr=u"@id"),
    _f("deliverer_name", u"Dostawca", G_BASIC, KIND_BLOCK, element=u"/deliverer", attr=u"@name",
       sources=XML_ONLY),
    _f("taxcode", u"Kod podatkowy", G_BASIC, KIND_VALUE, path=u"/taxcode"),
    _f("cntaric", u"Kod CN/TARIC", G_BASIC, KIND_VALUE, path=u"@cntaric",
       sources=XML_ONLY),
    _f("warranty_id", u"ID gwarancji", G_BASIC, KIND_BLOCK, element=u"/warranty",
       attr=u"@id"),
    _f("warranty_name", u"Gwarancja", G_BASIC, KIND_BLOCK, element=u"/warranty",
       attr=u"@name"),
    _f("warranty_type", u"Typ gwarancji", G_BASIC, KIND_BLOCK, element=u"/warranty",
       attr=u"@type", sources=XML_ONLY),
    _f("warranty_period", u"Okres gwarancji (miesiące)", G_BASIC, KIND_BLOCK,
       element=u"/warranty", attr=u"@period", type="number", sources=XML_ONLY),
    _f("note", u"Notatka", G_BASIC, KIND_VALUE, path=u"/note"),
    _f("priority_level", u"Priorytet", G_BASIC, KIND_BLOCK, element=u"/priority", attr=u"@level"),
    _f("group_id", u"ID grupy", G_BASIC, KIND_BLOCK, element=u"/group", attr=u"@id"),
    _f("size_chart_id", u"ID tabeli rozmiarów", G_BASIC, KIND_BLOCK,
       element=u"/size_chart", attr=u"@id"),

    # -- opis (zależny od języka) ------------------------------------------
    _f("name", u"Nazwa produktu", G_DESC, KIND_LANG, path=u"/description/name"),
    _f("short_desc", u"Opis skrócony", G_DESC, KIND_LANG, path=u"/description/short_desc"),
    _f("long_desc", u"Opis pełny", G_DESC, KIND_LANG, path=u"/description/long_desc"),
    _f("meta_title", u"Meta tytuł", G_DESC, KIND_LANG, path=u"/description/meta_title"),
    _f("meta_description", u"Meta opis", G_DESC, KIND_LANG, path=u"/description/meta_description"),
    _f("meta_keywords", u"Meta słowa kluczowe", G_DESC, KIND_LANG, path=u"/description/meta_keywords"),
    _f("pricecomparator_name", u"Nazwa do porównywarek", G_DESC, KIND_LANG,
       path=u"/description/pricecomparator_name"),
    _f("auction_name", u"Nazwa aukcyjna", G_DESC, KIND_LANG, path=u"/description/auction_name"),
    _f("auction_long_desc", u"Opis aukcyjny", G_DESC, KIND_LANG,
       path=u"/description/auction_long_desc"),

    # -- ceny (zależne od sklepu i rozmiaru) -------------------------------
    _f("price_gross", u"Cena brutto", G_PRICE, KIND_BLOCK, element=u"/price",
       attr=u"@gross", type="number"),
    _f("price_net", u"Cena netto", G_PRICE, KIND_BLOCK, element=u"/price",
       attr=u"@net", type="number"),
    _f("price_promotional_gross", u"Cena promocyjna brutto", G_PRICE, KIND_BLOCK,
       element=u"/price", attr=u"@promotional_gross", type="number"),
    _f("price_promotional_net", u"Cena promocyjna netto", G_PRICE, KIND_BLOCK,
       element=u"/price", attr=u"@promotional_net", type="number"),
    _f("srp_gross", u"Cena sugerowana brutto", G_PRICE, KIND_BLOCK, element=u"/srp",
       attr=u"@gross", type="number"),
    _f("price_retail_gross", u"Detaliczna brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_retail/site", attr=u"@gross", type="number"),
    _f("price_retail_net", u"Detaliczna netto", G_PRICE, KIND_BLOCK,
       element=u"/price_retail/site", attr=u"@net", type="number"),
    _f("price_retail_promotional_gross", u"Detaliczna promocyjna brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_retail/site", attr=u"@promotional_gross", type="number"),
    _f("promotion_id", u"ID promocji", G_PRICE, KIND_BLOCK, element=u"/promotion",
       attr=u"@id", sources=XML_ONLY),
    _f("promotion_name", u"Nazwa promocji", G_PRICE, KIND_BLOCK, element=u"/promotion",
       attr=u"@name", sources=XML_ONLY),
    _f("promotion_start", u"Początek promocji", G_PRICE, KIND_BLOCK,
       element=u"/promotion", attr=u"@start_date", type="date", sources=XML_ONLY),
    _f("promotion_normal_gross", u"Cena sprzed promocji brutto", G_PRICE, KIND_BLOCK,
       element=u"/promotion/price/normal_retail_price", attr=u"@gross", type="number",
       sources=XML_ONLY),
    _f("promotion_normal_net", u"Cena sprzed promocji netto", G_PRICE, KIND_BLOCK,
       element=u"/promotion/price/normal_retail_price", attr=u"@net", type="number",
       sources=XML_ONLY),
    _f("price_wholesale_gross", u"Hurtowa brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_wholesale/site", attr=u"@gross", type="number"),
    _f("price_minimal_gross", u"Minimalna brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_minimal/site", attr=u"@gross", type="number"),
    _f("price_pos_gross", u"POS brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_pos/price", attr=u"@gross", type="number"),
    _f("price_automatic_gross", u"Wyliczana automatycznie brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_automatic_calculation/site", attr=u"@gross", type="number"),
    _f("price_dynamic_gross", u"Detaliczna dynamiczna brutto", G_PRICE, KIND_BLOCK,
       element=u"/price_retail_dynamic/site", attr=u"@gross", type="number"),
    _f("pricecomparator_gross", u"Do porównywarek brutto", G_PRICE, KIND_BLOCK,
       element=u"/pricecomparator_price/site", attr=u"@gross", type="number"),
    _f("omnibus_retail_gross", u"Omnibus detaliczna brutto", G_PRICE, KIND_BLOCK,
       element=u"/omnibus_price_retail/site", attr=u"@gross", type="number",
       sources=XML_ONLY),
    _f("omnibus_wholesale_gross", u"Omnibus hurtowa brutto", G_PRICE, KIND_BLOCK,
       element=u"/omnibus_price_wholesale/site", attr=u"@gross", type="number",
       sources=XML_ONLY),
    _f("last_purchase_gross", u"Ostatnia cena zakupu brutto", G_PRICE, KIND_BLOCK,
       element=u"/last_purchase_price", attr=u"@gross", type="number", sources=XML_ONLY),
    _f("average_purchase_gross", u"Średnia cena zakupu brutto", G_PRICE, KIND_BLOCK,
       element=u"/average_purchase_price", attr=u"@gross", type="number", sources=XML_ONLY),

    # -- rozmiar -----------------------------------------------------------
    _f("size_id", u"ID rozmiaru", G_SIZE, KIND_SIZE, path=u"@id"),
    _f("size_name", u"Nazwa rozmiaru", G_SIZE, KIND_SIZE, path=u"@name"),
    _f("size_code", u"Kod rozmiaru", G_SIZE, KIND_SIZE, path=u"@code"),
    _f("size_code_external", u"Kod zewnętrzny rozmiaru", G_SIZE, KIND_SIZE, path=u"@code_external"),
    _f("size_code_producer", u"Kod producenta rozmiaru", G_SIZE, KIND_SIZE, path=u"@code_producer"),
    _f("size_weight", u"Waga rozmiaru", G_SIZE, KIND_SIZE, path=u"@weight", type="number"),
    _f("size_price_gross", u"Cena rozmiaru brutto", G_SIZE, KIND_SIZE,
       path=u"/price@gross", type="number"),
    _f("size_price_net", u"Cena rozmiaru netto", G_SIZE, KIND_SIZE,
       path=u"/price@net", type="number"),
    _f("size_price_promotional_gross", u"Cena promocyjna rozmiaru brutto", G_SIZE, KIND_SIZE,
       path=u"/price@promotional_gross", type="number"),
    _f("size_price_promotional_net", u"Cena promocyjna rozmiaru netto", G_SIZE, KIND_SIZE,
       path=u"/price@promotional_net", type="number"),
    _f("size_srp_gross", u"Sugerowana rozmiaru brutto", G_SIZE, KIND_SIZE,
       path=u"/srp@gross", type="number"),
    # Ta sama cena nazywa się inaczej w każdym z formatów.
    _f("size_crossedout_gross", u"Cena przekreślona brutto", G_SIZE, KIND_SIZE,
       path=u"/crossedout_retail_price@gross",
       alt_path=u"/strikethrough_retail_price@gross", type="number"),
    _f("size_crossedout_net", u"Cena przekreślona netto", G_SIZE, KIND_SIZE,
       path=u"/crossedout_retail_price@net",
       alt_path=u"/strikethrough_retail_price@net", type="number"),
    _f("size_quantity", u"Stan magazynowy", G_SIZE, KIND_SIZE,
       path=u"/stock@quantity", type="number"),
    _f("size_available_stock", u"Stan dostępny", G_SIZE, KIND_SIZE,
       path=u"/stock@available_stock_quantity", type="number", sources=XML_ONLY),
    _f("size_availability", u"Dostępność rozmiaru", G_SIZE, KIND_SIZE,
       path=u"@available", sources=XML_ONLY),

    # -- dostępność --------------------------------------------------------
    _f("availability_value", u"Dostępność", G_STOCK, KIND_BLOCK,
       element=u"/availability/site", attr=u"@value"),
    _f("availability_management", u"Zarządzanie dostępnością", G_STOCK, KIND_BLOCK,
       element=u"/availability_management", attr=u"@value"),
    _f("availability_profile_id", u"Profil dostępności", G_STOCK, KIND_BLOCK,
       element=u"/availability_profile", attr=u"@id"),
    _f("delivery_days", u"Czas dostawy (dni)", G_STOCK, KIND_BLOCK,
       element=u"/delivery_time/time", attr=u"@days", type="number"),
    _f("delivery_mode", u"Tryb dostawy", G_STOCK, KIND_BLOCK,
       element=u"/delivery_time/mode", attr=u"@type"),
    _f("sell_by_retail", u"Sprzedaż detaliczna po", G_STOCK, KIND_BLOCK,
       element=u"/sell_by/retail", attr=u"@quantity", type="number"),
    _f("inwrapper_quantity", u"Sztuk w opakowaniu", G_STOCK, KIND_BLOCK,
       element=u"/inwrapper", attr=u"@quantity", type="number"),
    _f("visibility_site", u"Widoczny w sklepie", G_STOCK, KIND_BLOCK,
       element=u"/visibility/site", attr=u"@visible"),
    _f("visibility_comparator", u"Widoczny w porównywarkach", G_STOCK, KIND_BLOCK,
       element=u"/visibility/price_comparator", attr=u"@visible"),
    _f("enable_in_pos", u"Włączony w POS", G_STOCK, KIND_BLOCK,
       element=u"/enable_in_pos", attr=u"@enabled"),
    _f("sum_in_basket", u"Sumowanie w koszyku", G_STOCK, KIND_BLOCK,
       element=u"/sum_in_basket", attr=u"@value"),

    # -- zdjęcia -----------------------------------------------------------
    _f("images_large", u"Zdjęcia duże", G_IMAGE, KIND_IMAGES, image_kind=u"large", multi=True),
    _f("images_icons", u"Ikona karty", G_IMAGE, KIND_IMAGES, image_kind=u"icons",
       multi=True),
    _f("images_medium", u"Zdjęcia średnie", G_IMAGE, KIND_IMAGES, image_kind=u"medium",
       multi=True, sources=XML_ONLY),
    _f("images_small", u"Zdjęcia małe", G_IMAGE, KIND_IMAGES, image_kind=u"small",
       multi=True, sources=XML_ONLY),
    _f("images_originals", u"Zdjęcia oryginalne", G_IMAGE, KIND_IMAGES,
       image_kind=u"originals", multi=True, sources=XML_ONLY),
    _f("images_auction_icon", u"Ikona aukcyjna", G_IMAGE, KIND_IMAGES,
       image_kind=u"auction_icon", multi=True, sources=CSV_ONLY),
    _f("images_group_icon", u"Ikona grupy", G_IMAGE, KIND_IMAGES,
       image_kind=u"group_icon", multi=True, sources=CSV_ONLY),

    # -- daty --------------------------------------------------------------
    _f("date_created", u"Data utworzenia", G_DATE, KIND_BLOCK,
       element=u"/date_created", attr=u"@datetime", type="date", sources=XML_ONLY),
    _f("modification_date", u"Data modyfikacji", G_DATE, KIND_BLOCK,
       element=u"/modification_date", attr=u"@datetime", type="date", sources=XML_ONLY),
    _f("expiry_date", u"Data ważności", G_DATE, KIND_BLOCK,
       element=u"/expiry_date", attr=u"@datetime", type="date", sources=XML_ONLY),

    # -- podmiot odpowiedzialny (GPSR) -------------------------------------
    # Komplet pól obu podmiotów: producenta i osoby odpowiedzialnej w UE.
    # W CSV identyfikator ma ukośnik przed małpą (`/producer/@id`), w XML jest
    # zwykłym atrybutem - stąd druga ścieżka.
    _f("entity_producer_id", u"Producent - identyfikator", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/@id", alt_path=u"/responsible_entity/producer@id"),
    _f("entity_producer_code", u"Producent - kod", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/code"),
    _f("entity_producer_name", u"Producent - nazwa", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/name"),
    _f("entity_producer_mail", u"Producent - e-mail", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/mail"),
    _f("entity_producer_phone", u"Producent - telefon", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/phone"),
    _f("entity_producer_url", u"Producent - strona", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/url"),
    _f("entity_producer_description", u"Producent - opis", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/description"),
    _f("entity_producer_country", u"Producent - kraj", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/country"),
    _f("entity_producer_city", u"Producent - miasto", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/city"),
    _f("entity_producer_zipcode", u"Producent - kod pocztowy", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/zipcode"),
    _f("entity_producer_street", u"Producent - ulica", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/street"),
    _f("entity_producer_number", u"Producent - numer domu", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/number"),
    _f("entity_producer_subnumber", u"Producent - numer lokalu", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/producer/subnumber"),
    _f("entity_person_id", u"Osoba odpowiedzialna - identyfikator", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/@id", alt_path=u"/responsible_entity/persons/person@id"),
    _f("entity_person_code", u"Osoba odpowiedzialna - kod", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/code"),
    _f("entity_person_name", u"Osoba odpowiedzialna - nazwa", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/name"),
    _f("entity_person_mail", u"Osoba odpowiedzialna - e-mail", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/mail"),
    _f("entity_person_phone", u"Osoba odpowiedzialna - telefon", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/phone"),
    _f("entity_person_url", u"Osoba odpowiedzialna - strona", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/url"),
    _f("entity_person_description", u"Osoba odpowiedzialna - opis", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/description"),
    _f("entity_person_country", u"Osoba odpowiedzialna - kraj", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/country"),
    _f("entity_person_city", u"Osoba odpowiedzialna - miasto", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/city"),
    _f("entity_person_zipcode", u"Osoba odpowiedzialna - kod pocztowy", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/zipcode"),
    _f("entity_person_street", u"Osoba odpowiedzialna - ulica", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/street"),
    _f("entity_person_number", u"Osoba odpowiedzialna - numer domu", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/number"),
    _f("entity_person_subnumber", u"Osoba odpowiedzialna - numer lokalu", G_ENTITY, KIND_VALUE,
       path=u"/responsible_entity/persons/person/subnumber"),

    # -- opinie (tylko XML - CSV z panelu ich nie zawiera) -----------------
    # W IOF nie ma gotowych statystyk, są pojedyncze opinie. Czytnik liczy je
    # w locie i podaje tutaj jako wartości gotowe do wystawienia w feedzie.
    _f("opinions_count", u"Liczba opinii", G_OPINION, KIND_VALUE,
       path=u"/opinions@count", type="number", sources=XML_ONLY),
    _f("opinions_confirmed", u"Liczba opinii potwierdzonych", G_OPINION, KIND_VALUE,
       path=u"/opinions@confirmed", type="number", sources=XML_ONLY),
    _f("opinions_average", u"Średnia ocena", G_OPINION, KIND_VALUE,
       path=u"/opinions@average", type="number", sources=XML_ONLY),
    _f("opinions_note_5", u"Ocen na 5", G_OPINION, KIND_VALUE,
       path=u"/opinions@note_5", type="number", sources=XML_ONLY),
    _f("opinions_note_4", u"Ocen na 4", G_OPINION, KIND_VALUE,
       path=u"/opinions@note_4", type="number", sources=XML_ONLY),
    _f("opinions_note_3", u"Ocen na 3", G_OPINION, KIND_VALUE,
       path=u"/opinions@note_3", type="number", sources=XML_ONLY),
    _f("opinions_note_2", u"Ocen na 2", G_OPINION, KIND_VALUE,
       path=u"/opinions@note_2", type="number", sources=XML_ONLY),
    _f("opinions_note_1", u"Ocen na 1", G_OPINION, KIND_VALUE,
       path=u"/opinions@note_1", type="number", sources=XML_ONLY),
    _f("opinions_last_date", u"Data ostatniej opinii", G_OPINION, KIND_VALUE,
       path=u"/opinions@last_date", type="date", sources=XML_ONLY),
]

#: Pole-znacznik: wszystkie parametry, rozbijane przez expander.
PARAMS_FIELD = _f("params", u"Parametry produktu", G_PARAM, KIND_PARAMS, multi=True)


class Registry(object):
    """Rdzeń plus pola wykryte w konkretnym pliku."""

    def __init__(self, fields=None):
        self.fields = list(fields if fields is not None else CORE_FIELDS)
        self.fields.append(PARAMS_FIELD)
        self._by_id = dict((f.id, f) for f in self.fields)

    def get(self, field_id):
        return self._by_id.get(field_id)

    def add(self, field):
        if field.id in self._by_id:
            return self._by_id[field.id]
        self.fields.append(field)
        self._by_id[field.id] = field
        return field

    def groups(self, source_type=None):
        """Pola pogrupowane, w kolejności deklaracji. Nic nie znika - tylko oznaczamy."""
        order = []
        buckets = {}
        for field in self.fields:
            if field.group not in buckets:
                buckets[field.group] = []
                order.append(field.group)
            buckets[field.group].append(field)
        return [(name, buckets[name]) for name in order]

    def known_paths(self):
        paths = set()
        for field in self.fields:
            if field.path:
                paths.add(field.path)
            if field.element:
                paths.add(field.element + (field.attr or u""))
        return paths

    def add_unknown_column(self, header):
        """Kolumna spoza rdzenia - ląduje w 'Nierozpoznane' z surową nazwą."""
        field_id = u"raw:" + header
        if field_id in self._by_id:
            return self._by_id[field_id]
        return self.add(Field(field_id, header, G_OTHER, KIND_VALUE, path=header,
                              dynamic=True, note=u"kolumna wykryta w pliku"))


def build_registry():
    return Registry()
