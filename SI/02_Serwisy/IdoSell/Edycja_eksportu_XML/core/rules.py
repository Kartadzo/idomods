# -*- coding: utf-8 -*-
"""Reguły przetwarzania wartości.

Reguła działa na jednej kolumnie wyjściowej, po ekstrakcji i rozbiciu kolekcji,
a przed zapisem:

    JEŻELI <warunek>  TO  <akcja>

Warunek jest opcjonalny i może badać inną kolumnę niż ta, którą reguła zmienia.
Filtry rekordów to ten sam mechanizm warunków, tylko zamiast zmieniać wartość
odrzucają cały wiersz.

Wszystko jest serializowalne do JSON, bo profil użytkownika musi dać się zapisać
i odtworzyć.
"""

import re

# -- operatory warunków -----------------------------------------------------

OPERATORS = [
    ("eq", u"równa się"),
    ("ne", u"różne od"),
    ("contains", u"zawiera"),
    ("not_contains", u"nie zawiera"),
    ("starts", u"zaczyna się od"),
    ("ends", u"kończy się na"),
    ("regex", u"pasuje do wyrażenia"),
    ("empty", u"jest puste"),
    ("not_empty", u"nie jest puste"),
    ("gt", u"większe niż"),
    ("lt", u"mniejsze niż"),
    ("in_list", u"jest na liście"),
]

OPERATOR_LABELS = dict(OPERATORS)

# -- akcje ------------------------------------------------------------------

ACTIONS = [
    ("set", u"ustaw stałą"),
    ("map", u"mapuj wartości"),
    ("regex_replace", u"szukaj i zamień"),
    ("prefix", u"dodaj przedrostek"),
    ("suffix", u"dodaj przyrostek"),
    ("template", u"złóż z kilku kolumn"),
    ("fallback", u"pierwsza niepusta z kolumn"),
    ("truncate", u"przytnij do N znaków"),
    ("strip_html", u"usuń znaczniki HTML"),
    ("collapse_ws", u"scal białe znaki"),
    ("case", u"zmień wielkość liter"),
    ("number", u"przelicz liczbę"),
    ("date_format", u"sformatuj datę"),
    ("pick", u"weź n-tą wartość"),
    ("join", u"połącz wartości"),
    ("blank", u"wyczyść"),
]

ACTION_LABELS = dict(ACTIONS)

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
_PLACEHOLDER = re.compile(r"\{([^{}]+)\}")


def _text(value):
    if value is None:
        return u""
    if isinstance(value, list):
        return u", ".join([_text(v) for v in value])
    return value if isinstance(value, str) else u"%s" % value


def _resolve_key(row, field):
    """Klucz wiersza odpowiadający nazwie kolumny zapisanej w regule.

    Przełącznik pisowni nagłówków zmienia `nazwa` na `Nazwa`, a reguła zapisana
    wcześniej wskazuje starą postać. Dopasowanie bez względu na wielkość liter
    sprawia, że przełącznik nie unieważnia reguł ani filtrów.
    """
    if field in row:
        return field
    lowered = (field or u"").lower()
    for key in row:
        if key.lower() == lowered:
            return key
    return None


def _lookup(row, field, default=u""):
    key = _resolve_key(row, field)
    return default if key is None else row.get(key, default)


def _number(value):
    text = _text(value).strip().replace(u" ", u"").replace(u",", u".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


class Condition(object):
    """Pojedynczy test na wartości kolumny."""

    def __init__(self, field=u"", op="not_empty", value=u"", case_sensitive=False):
        self.field = field
        self.op = op
        self.value = value
        self.case_sensitive = case_sensitive

    def evaluate(self, row):
        actual = _text(_lookup(row, self.field))
        expected = _text(self.value)
        if not self.case_sensitive:
            actual_cmp = actual.lower()
            expected_cmp = expected.lower()
        else:
            actual_cmp, expected_cmp = actual, expected

        op = self.op
        if op == "empty":
            return not actual.strip()
        if op == "not_empty":
            return bool(actual.strip())
        if op == "eq":
            return actual_cmp == expected_cmp
        if op == "ne":
            return actual_cmp != expected_cmp
        if op == "contains":
            return expected_cmp in actual_cmp
        if op == "not_contains":
            return expected_cmp not in actual_cmp
        if op == "starts":
            return actual_cmp.startswith(expected_cmp)
        if op == "ends":
            return actual_cmp.endswith(expected_cmp)
        if op == "regex":
            flags = 0 if self.case_sensitive else re.IGNORECASE
            try:
                return re.search(expected, actual, flags) is not None
            except re.error:
                return False
        if op == "in_list":
            items = [i.strip() for i in expected.replace(u"|", u",").split(u",")]
            if not self.case_sensitive:
                items = [i.lower() for i in items]
            return actual_cmp in items
        if op in ("gt", "lt"):
            left, right = _number(actual), _number(expected)
            if left is None or right is None:
                return False
            return left > right if op == "gt" else left < right
        return False

    def to_dict(self):
        return {"field": self.field, "op": self.op, "value": self.value,
                "case_sensitive": self.case_sensitive}

    @staticmethod
    def from_dict(data):
        return Condition(data.get("field", u""), data.get("op", "not_empty"),
                         data.get("value", u""), data.get("case_sensitive", False))

    def describe(self):
        label = OPERATOR_LABELS.get(self.op, self.op)
        if self.op in ("empty", "not_empty"):
            return u"%s %s" % (self.field, label)
        return u"%s %s „%s”" % (self.field, label, _text(self.value))


class ConditionGroup(object):
    """Warunki łączone spójnikiem. Pusta grupa znaczy 'zawsze'."""

    def __init__(self, mode="and", conditions=None):
        self.mode = mode
        self.conditions = list(conditions or [])

    def evaluate(self, row):
        if not self.conditions:
            return True
        results = [c.evaluate(row) for c in self.conditions]
        return all(results) if self.mode == "and" else any(results)

    def to_dict(self):
        return {"mode": self.mode, "conditions": [c.to_dict() for c in self.conditions]}

    @staticmethod
    def from_dict(data):
        if not data:
            return ConditionGroup()
        return ConditionGroup(data.get("mode", "and"),
                              [Condition.from_dict(c) for c in data.get("conditions", [])])

    def describe(self):
        if not self.conditions:
            return u"zawsze"
        joiner = u" oraz " if self.mode == "and" else u" lub "
        return joiner.join([c.describe() for c in self.conditions])


class Rule(object):
    """Jedna reguła: warunek plus akcja na wskazanej kolumnie."""

    def __init__(self, field=u"", action="set", params=None, condition=None, enabled=True):
        self.field = field
        self.action = action
        self.params = dict(params or {})
        self.condition = condition or ConditionGroup()
        self.enabled = enabled

    def apply(self, row):
        key = _resolve_key(row, self.field)
        if not self.enabled or key is None:
            return
        if not self.condition.evaluate(row):
            return
        row[key] = self._run(row.get(key, u""), row)

    def _run(self, value, row):
        action = self.action
        params = self.params
        text = _text(value)

        if action == "set":
            return _text(params.get("value", u""))
        if action == "blank":
            return u""
        if action == "map":
            mapping = params.get("mapping") or {}
            if text in mapping:
                return _text(mapping[text])
            lowered = dict((_text(k).lower(), v) for k, v in mapping.items())
            if text.lower() in lowered:
                return _text(lowered[text.lower()])
            if params.get("keep_unmapped", True):
                return text
            return _text(params.get("default", u""))
        if action == "regex_replace":
            try:
                flags = 0 if params.get("case_sensitive") else re.IGNORECASE
                return re.sub(params.get("pattern", u""), params.get("replacement", u""),
                              text, flags=flags)
            except re.error:
                return text
        if action == "prefix":
            return _text(params.get("value", u"")) + text
        if action == "suffix":
            return text + _text(params.get("value", u""))
        if action == "template":
            return _fill_template(_text(params.get("template", u"")), row)
        if action == "fallback":
            if text.strip():
                return text
            for name in params.get("fields", []):
                candidate = _text(_lookup(row, name))
                if candidate.strip():
                    return candidate
            return _text(params.get("default", u""))
        if action == "truncate":
            return _truncate(text, int(params.get("length", 100) or 100),
                             bool(params.get("on_word", True)),
                             _text(params.get("ellipsis", u"")))
        if action == "strip_html":
            return _WS.sub(u" ", _TAG.sub(u" ", text)).strip()
        if action == "collapse_ws":
            return _WS.sub(u" ", text).strip()
        if action == "case":
            style = params.get("style", "lower")
            if style == "upper":
                return text.upper()
            if style == "title":
                return text.title()
            if style == "sentence":
                stripped = text.strip()
                return stripped[:1].upper() + stripped[1:].lower() if stripped else u""
            return text.lower()
        if action == "number":
            return _number_action(text, params)
        if action == "date_format":
            return _date_action(text, params)
        if action == "pick":
            parts = _as_list(value, params.get("separator", u"\n"))
            index = int(params.get("index", 1) or 1) - 1
            if 0 <= index < len(parts):
                return parts[index]
            return u""
        if action == "join":
            parts = _as_list(value, params.get("separator", u"\n"))
            return _text(params.get("glue", u", ")).join(parts)
        return text

    def to_dict(self):
        return {"field": self.field, "action": self.action, "params": self.params,
                "condition": self.condition.to_dict(), "enabled": self.enabled}

    @staticmethod
    def from_dict(data):
        return Rule(data.get("field", u""), data.get("action", "set"),
                    data.get("params"), ConditionGroup.from_dict(data.get("condition")),
                    data.get("enabled", True))

    def describe(self):
        label = ACTION_LABELS.get(self.action, self.action)
        detail = u""
        if self.action in ("set", "prefix", "suffix"):
            detail = u" „%s”" % _text(self.params.get("value", u""))
        elif self.action == "truncate":
            detail = u" do %s znaków" % self.params.get("length", 100)
        elif self.action == "template":
            detail = u" „%s”" % _text(self.params.get("template", u""))
        elif self.action == "map":
            detail = u" (%d wpisów)" % len(self.params.get("mapping") or {})
        elif self.action == "regex_replace":
            detail = u" „%s” → „%s”" % (self.params.get("pattern", u""),
                                        self.params.get("replacement", u""))
        return u"%s: %s%s  [gdy %s]" % (self.field, label, detail, self.condition.describe())


class RecordFilter(object):
    """Filtr rekordów - odrzuca cały wiersz, zamiast zmieniać wartość."""

    def __init__(self, condition=None, mode="skip", enabled=True, label=u""):
        self.condition = condition or ConditionGroup()
        self.mode = mode          # 'skip' - pomiń gdy prawda, 'keep' - zostaw tylko gdy prawda
        self.enabled = enabled
        self.label = label

    def rejects(self, row):
        if not self.enabled or not self.condition.conditions:
            return False
        matched = self.condition.evaluate(row)
        return matched if self.mode == "skip" else not matched

    def to_dict(self):
        return {"condition": self.condition.to_dict(), "mode": self.mode,
                "enabled": self.enabled, "label": self.label}

    @staticmethod
    def from_dict(data):
        return RecordFilter(ConditionGroup.from_dict(data.get("condition")),
                            data.get("mode", "skip"), data.get("enabled", True),
                            data.get("label", u""))

    def describe(self):
        verb = u"pomiń gdy" if self.mode == "skip" else u"zostaw tylko gdy"
        return u"%s %s" % (verb, self.condition.describe())


class RuleSet(object):
    """Reguły i filtry stosowane po kolei do każdego wiersza."""

    def __init__(self, rules=None, filters=None):
        self.rules = list(rules or [])
        self.filters = list(filters or [])
        self.skipped = 0

    def accepts(self, row):
        for record_filter in self.filters:
            if record_filter.rejects(row):
                self.skipped += 1
                return False
        return True

    def apply(self, row):
        for rule in self.rules:
            rule.apply(row)
        return row

    def to_dict(self):
        return {"rules": [r.to_dict() for r in self.rules],
                "filters": [f.to_dict() for f in self.filters]}

    @staticmethod
    def from_dict(data):
        if not data:
            return RuleSet()
        return RuleSet([Rule.from_dict(r) for r in data.get("rules", [])],
                       [RecordFilter.from_dict(f) for f in data.get("filters", [])])


# -- pomocnicze -------------------------------------------------------------

def _as_list(value, separator):
    if isinstance(value, list):
        return [v for v in value]
    text = _text(value)
    if not text:
        return []
    return text.split(separator) if separator else [text]


def _fill_template(template, row):
    def replace(match):
        return _text(_lookup(row, match.group(1)))
    return _PLACEHOLDER.sub(replace, template)


def _truncate(text, length, on_word, ellipsis):
    if length <= 0 or len(text) <= length:
        return text
    limit = length - len(ellipsis)
    if limit <= 0:
        return text[:length]
    cut = text[:limit]
    if on_word and u" " in cut:
        cut = cut.rsplit(u" ", 1)[0]
    return cut.rstrip() + ellipsis


def _number_action(text, params):
    number = _number(text)
    if number is None:
        return text
    factor = _number(params.get("multiply"))
    if factor is not None:
        number *= factor
    addend = _number(params.get("add"))
    if addend is not None:
        number += addend
    decimals = params.get("decimals")
    if decimals in (None, u""):
        formatted = (u"%g" % number)
    else:
        formatted = u"%.*f" % (int(decimals), number)
    separator = params.get("decimal_separator")
    if separator:
        formatted = formatted.replace(u".", separator)
    return formatted


def _date_action(text, params):
    from datetime import datetime
    source = params.get("input_format") or u"%Y-%m-%d %H:%M:%S"
    target = params.get("output_format") or u"%Y-%m-%d"
    candidate = text.strip()
    if not candidate:
        return u""
    for pattern in (source, u"%Y-%m-%d %H:%M:%S", u"%Y-%m-%d", u"%d.%m.%Y"):
        try:
            return datetime.strptime(candidate, pattern).strftime(target)
        except ValueError:
            continue
    return text
