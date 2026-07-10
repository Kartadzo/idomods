#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SummonFeed XSLT Generator
Aplikacja do generowania sterowników XSLT na podstawie wybranych struktur i parametrów.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class SummonFeedGenerator:
    """Główna klasa aplikacji do generowania XSLT."""
    
    def __init__(self):
        """Inicjalizacja ścieżek i załadowanie danych."""
        self.base_path = Path(__file__).parent
        self.structures_path = self.base_path / "structure_templates"
        self.parameters_path = self.base_path / "parameters_templates"
        self.variables_path = self.base_path / "variables"
        self.helpers_path = self.base_path / "helpers"
        self.lang_path = self.base_path / "lang"
        self.output_path = self.base_path

        self.structures: Dict = {}
        self.parameters: Dict = {}
        self.variables_registry: Dict = {}
        self.helpers_registry: Dict = {}
        self.languages: Dict[str, Dict] = {}
        self.selected_structure: Optional[Dict] = None
        self.selected_params: Dict[str, List[Dict]] = {}
        self.lang: str = 'pl'
        self.output_overrides: Dict[str, str] = {}
        self.prefix_override: Optional[str] = None

        self._load_data()

    def t(self, key: str, **kwargs) -> str:
        """Zwróć tekst UI w wybranym języku (z opcjonalnym format())."""
        strings = self.languages.get(self.lang) or next(iter(self.languages.values()), {})
        text = strings.get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _desc(self, data: Dict) -> str:
        """Opis parametru/struktury w wybranym języku (fallback na angielski)."""
        if self.lang == 'pl':
            return data.get('description_pl') or data.get('description', '')
        return data.get('description', '') or data.get('description_pl', '')
    
    def _load_data(self) -> None:
        """Wczytaj wszystkie struktury i parametry JSON.
        Pliki zaczynające się od '_' są pomijane (szablony, rejestry, notatki)."""
        # Wczytaj struktury
        for json_file in self.structures_path.glob("*.json"):
            if json_file.name.startswith('_'):
                continue
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                structure_name = data['name']
                self.structures[structure_name] = {
                    'data': data,
                    'json_path': json_file,
                    'xsl_path': json_file.with_suffix('.xsl')
                }

        # Wczytaj parametry
        for json_file in self.parameters_path.glob("*.json"):
            if json_file.name.startswith('_'):
                continue
            with open(json_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    param_name = data['name']
                    self.parameters[param_name] = {
                        'data': data,
                        'json_path': json_file,
                        'xsl_path': json_file.with_suffix('.xsl')
                    }
                except json.JSONDecodeError:
                    print(f"⚠️  Błąd w pliku {json_file.name}, pomijam...")

        # Wczytaj rejestr zmiennych (variables/_registry.json), jeśli istnieje
        registry_file = self.variables_path / "_registry.json"
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.variables_registry = {
                    k: v for k, v in data.items() if not k.startswith('_')
                }

        # Wczytaj rejestr helperów (helpers/_registry.json), jeśli istnieje
        helpers_registry_file = self.helpers_path / "_registry.json"
        if helpers_registry_file.exists():
            with open(helpers_registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.helpers_registry = {
                    k: v for k, v in data.items() if not k.startswith('_')
                }

        # Wczytaj pliki językowe (lang/*.json) — kod języka = nazwa pliku
        if self.lang_path.exists():
            for lang_file in sorted(self.lang_path.glob("*.json")):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.languages[lang_file.stem] = json.load(f)
        if self.lang not in self.languages and self.languages:
            self.lang = next(iter(self.languages))
    
    def _clear_screen(self) -> None:
        """Wyczyść ekran terminala."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self, title: str) -> None:
        """Wydrukuj nagłówek."""
        self._clear_screen()
        print("=" * 70)
        print(f"  {title}")
        print("=" * 70)
        print()
    
    def _choose_language(self) -> bool:
        """Krok 0: wybór języka interfejsu (dynamicznie z folderu lang/). False = wyjście."""
        codes = list(self.languages.keys())
        if not codes:
            return True  # brak plików językowych — działaj na domyślnym
        header = self.languages[codes[0]].get('header_lang', 'JĘZYK / LANGUAGE')
        self._print_header(header)
        for i, code in enumerate(codes, 1):
            name = self.languages[code].get('_name', code)
            print(f"{i}. {name}")
        print()
        print("0. Wyjście / Exit")
        print()
        while True:
            choice = input("Wybierz / Choose [1]: ").strip()
            if choice == '0':
                return False
            if choice == '':
                self.lang = codes[0]
                return True
            if choice.isdigit() and 1 <= int(choice) <= len(codes):
                self.lang = codes[int(choice) - 1]
                return True
            print("❌ " + " / ".join(str(i) for i in range(1, len(codes) + 1)) + " / 0")

    def _show_structure_menu(self) -> Optional[str]:
        """Pokaż menu wyboru struktury."""
        self._print_header(self.t('header_structure'))

        structures_list = list(self.structures.keys())

        if not structures_list:
            print(self.t('no_structures'))
            return None

        for i, name in enumerate(structures_list, 1):
            desc = self._desc(self.structures[name]['data'])
            print(f"{i}. {name}")
            print(f"   └─ {desc}")
            print()

        print(f"0. {self.t('exit')}")
        print()

        while True:
            try:
                choice = int(input(self.t('choose_number')).strip())
                if choice == 0:
                    return None
                if 1 <= choice <= len(structures_list):
                    return structures_list[choice - 1]
                print(self.t('invalid_choice'))
            except ValueError:
                print(self.t('invalid_number'))
    
    def _filter_parameters_for_structure(self, structure_name: str) -> Dict[str, List[str]]:
        """Filtruj parametry pasujące do wybranej struktury."""
        filtered = {}
        
        for param_name, param_info in self.parameters.items():
            param_data = param_info['data']
            
            # Sprawdź czy struktura jest obsługiwana
            if structure_name not in param_data.get('structure', []):
                continue
            
            # Pogrupuj parametry wg kontekstu
            context = param_data.get('context', 'unknown')
            if context not in filtered:
                filtered[context] = []
            
            filtered[context].append(param_name)
        
        return filtered
    
    def _show_parameters_menu(self, available_params: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Pokaż menu wyboru parametrów."""
        self._print_header(self.t('header_params'))

        selected = {}

        for context, param_names in sorted(available_params.items()):
            print("\n" + self.t('context', context=context))
            print("-" * 70)

            # Wyświetl dostępne parametry
            for i, param_name in enumerate(param_names, 1):
                param_data = self.parameters[param_name]['data']
                print(f"{i}. {param_name}: {self._desc(param_data)}")

            print()
            print(self.t('params_hint'))

            while True:
                try:
                    user_input = input(self.t('choice_for', context=context)).strip()

                    if not user_input:  # Pomiń ten kontekst
                        break

                    choices = [int(x.strip()) for x in user_input.split()]

                    # Waliduj wybory
                    if all(1 <= c <= len(param_names) for c in choices):
                        selected[context] = [param_names[c - 1] for c in choices]
                        break
                    else:
                        print(self.t('out_of_range'))
                except ValueError:
                    print(self.t('invalid_numbers'))

        return selected

    def _ask_output_names(self, selected: Dict[str, List[str]]) -> None:
        """Pozwól nadpisać prefiks 'g:' oraz nazwę elementu wyjściowego każdego parametru
        (Enter = domyślne)."""
        self.output_overrides = {}
        self.prefix_override = None
        params = [p for plist in selected.values() for p in plist]
        if not params:
            return
        self._print_header(self.t('header_output'))

        # Globalny prefiks elementów (namespace g:).
        #   Enter → zostaw 'g'; '-' → brak prefiksu; inne → nowy prefiks
        raw_prefix = input(self.t('ask_prefix', current='g')).strip()
        if raw_prefix == '-':
            self.prefix_override = ''            # brak jakiegokolwiek prefiksu
        else:
            new_prefix = raw_prefix.rstrip(':')
            if new_prefix and new_prefix != 'g':
                self.prefix_override = new_prefix

        print()
        print(self.t('output_hint'))
        print()
        for param_name in params:
            default_out = self.parameters[param_name]['data'].get('output', '')
            custom = input(self.t('ask_output_name', param=param_name, default=default_out)).strip()
            if custom and custom != default_out:
                self.output_overrides[param_name] = custom

    def _apply_prefix_override(self, xsl: str) -> str:
        """Zmień prefiks przestrzeni nazw 'g' zgodnie z wyborem użytkownika.
        None / 'g' → bez zmian; '' → brak prefiksu (usuwa xmlns:g i g:);
        inny → nowy prefiks (spójnie: deklaracja xmlns:g oraz użycia g:)."""
        new = self.prefix_override
        if new is None or new == 'g':
            return xsl
        if new == '':
            # brak prefiksu: usuń deklaracje xmlns:g i prefiks g: z nazw elementów
            xsl = re.sub(r'\s+xmlns:g="[^"]*"', '', xsl)
            xsl = xsl.replace('g:', '')
            return xsl
        xsl = xsl.replace('xmlns:g=', f'xmlns:{new}=')
        xsl = xsl.replace('g:', f'{new}:')
        return xsl
    
    def _read_xslt_file(self, xsl_path: Path) -> str:
        """Wczytaj zawartość pliku XSLT."""
        try:
            with open(xsl_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Nie znaleziono pliku: {xsl_path}")
            return ""

    def _apply_output_override(self, param_name: str, content: str) -> str:
        """Zamień domyślną nazwę elementu wyjściowego na nazwę podaną przez użytkownika.
        Obsługuje formy: <xsl:element name="X">, <X> oraz </X>."""
        custom = self.output_overrides.get(param_name)
        if not custom:
            return content
        default = self.parameters[param_name]['data'].get('output', '')
        if not default or custom == default:
            return content
        content = content.replace(f'name="{default}"', f'name="{custom}"')
        content = content.replace(f"name='{default}'", f"name='{custom}'")
        content = content.replace(f'<{default}>', f'<{custom}>')
        content = content.replace(f'</{default}>', f'</{custom}>')
        return content
    
    # ---------------------------------------------------------
    #  OBSŁUGA CONFIGVARS
    # ---------------------------------------------------------

    def _get_config_vars(self, param_name: str) -> List[Dict]:
        return self.parameters[param_name]['data'].get('configVars', [])

    def _ask_for_config_vars(self, config_vars: List[Dict]) -> Dict[str, str]:
        values = {}
        if not config_vars:
            return values

        print("\n" + self.t('configvars_header') + "\n")

        for var in config_vars:
            values[var['name']] = self._ask_single_config_var(var)

        return values


    def _apply_config_vars_to_xslt(self, xslt: str, config_values: Dict[str, str]) -> str:
        for name, value in config_values.items():
            pattern = fr"<xsl:variable name=['\"]{name}['\"]>.*?</xsl:variable>"
            replacement = f"<xsl:variable name='{name}'>{value}</xsl:variable>"
            # callable replacement — nie interpretuje backslashy w treści (np. \GRATIS\)
            xslt = re.sub(pattern, lambda m, r=replacement: r, xslt, flags=re.DOTALL)
        return xslt

    # ---------------------------------------------------------
    #  WCZYTYWANIE SZABLONU PARAMETRU
    # ---------------------------------------------------------

    def _get_template_content(self, param_name: str) -> str:
        info = self.parameters[param_name]
        xsl_path = info['xsl_path']

        content = self._read_xslt_file(xsl_path).strip()

        # obsługa configVars
        config_vars = self._get_config_vars(param_name)
        if config_vars:
            config_values = self._ask_for_config_vars(config_vars)
            content = self._apply_config_vars_to_xslt(content, config_values)

        return content
    
    def _is_migrated(self, param_name: str) -> bool:
        """Parametr jest 'zmigrowany', jeśli wszystkie jego createVars są w rejestrze
        variables/. Wtedy zmienne (i configVars) wstrzykujemy centralnie z preambułu,
        a jego .xsl to sama emisja. W przeciwnym razie działa stara ścieżka (inline)."""
        create_vars = self.parameters[param_name]['data'].get('createVars', [])
        if not create_vars:
            return False
        return all(name in self.variables_registry for name in create_vars)

    def _ask_single_config_var(self, var: Dict) -> str:
        """Zapytaj o wartość pojedynczej configVar i sformatuj wg separatora."""
        name = var['name']
        default = var.get('default', '')
        delimeter = var.get('delimeter', '')

        # Bez separatora → pojedyncza wartość (Enter = domyślna)
        if not delimeter:
            user_input = input(self.t('ask_configvar', name=name, default=default)).strip()
            return user_input if user_input else default

        # Z separatorem → tryb fraza-po-frazie (obsługuje nazwy wielowyrazowe)
        print(self.t('configvar_list_intro', name=name, default=default))
        phrases: List[str] = []
        while True:
            phrase = input(self.t('configvar_phrase', n=len(phrases) + 1)).strip()
            if not phrase:
                break
            phrases.append(phrase)

        # Brak wpisów → wartość domyślna (w JSON już otoczona separatorem)
        if not phrases:
            return default
        return delimeter + delimeter.join(phrases) + delimeter

    def _build_variable_preamble(self, migrated_params: List[str]) -> str:
        """Zbuduj preambuł zmiennych dla parametrów zmigrowanych w danym kontekście:
        1) zdeduplikowane configVars (deklaracje generowane z metadanych),
        2) createVars: domknięcie zależności → sort po 'order' → dedup,
        w tej kolejności (configVars przed createVars, bo createVars ich używają)."""
        if not migrated_params:
            return ""

        lines: List[str] = []

        # 1) configVars — dedup po nazwie, wartość pytana raz
        seen_cfg: Dict[str, str] = {}
        for param_name in migrated_params:
            for var in self.parameters[param_name]['data'].get('configVars', []):
                if var['name'] in seen_cfg:
                    continue
                seen_cfg[var['name']] = self._ask_single_config_var(var)
        for name, value in seen_cfg.items():
            lines.append(f"      <xsl:variable name='{name}'>{value}</xsl:variable>")

        # 2) createVars — domknięcie + sort po order + dedup
        needed: List[str] = []
        seen: set = set()

        def add_closure(nm: str) -> None:
            if nm in seen or nm not in self.variables_registry:
                return
            for dep in self.variables_registry[nm].get('uses', []):
                add_closure(dep)
            if nm not in seen:
                seen.add(nm)
                needed.append(nm)

        for param_name in migrated_params:
            for nm in self.parameters[param_name]['data'].get('createVars', []):
                add_closure(nm)

        # stabilny sort utrzyma kolejność domknięcia przy remisach 'order'
        needed.sort(key=lambda n: self.variables_registry[n].get('order', 0))

        for nm in needed:
            frag = self._read_xslt_file(self.variables_path / f"{nm}.xsl").strip()
            lines.append(f"      {frag}")

        return "\n".join(lines) + "\n" if lines else ""

    def _build_xslt_structure(self) -> str:
        """Zbuduj ostateczny plik XSLT."""
        structure_data = self.selected_structure['data']
        base_xsl = self._read_xslt_file(self.selected_structure['xsl_path'])

        # Znajdź i wypełnij każdy insertion point
        for insertion_point in structure_data.get('insertionPoints', []):
            template_name = insertion_point['template']
            context = insertion_point['context']

            params = self.selected_params.get(context, [])
            migrated = [p for p in params if self._is_migrated(p)]

            # Zbierz kod dla tego kontekstu
            template_body = ""

            # preambuł zmiennych (tylko dla parametrów zmigrowanych)
            template_body += self._build_variable_preamble(migrated)

            # fragmenty emisji
            for param_name in params:
                if param_name in migrated:
                    # .xsl zmigrowanego parametru to sama emisja (bez deklaracji zmiennych)
                    param_content = self._read_xslt_file(
                        self.parameters[param_name]['xsl_path']).strip()
                else:
                    # stara ścieżka: inline configVars w .xsl
                    param_content = self._get_template_content(param_name)
                # opcjonalne nadpisanie nazwy elementu wyjściowego
                param_content = self._apply_output_override(param_name, param_content)
                template_body += f"      <!-- {param_name} -->\n"
                template_body += f"      {param_content}\n"

            # Wymień pusty template na wypełniony (callable — treść może mieć backslashe)
            pattern = (
               rf'(<xsl:template[^>]*name="{template_name}"[^>]*>)'
               r'\s*</xsl:template>'
            )
            body = template_body
            base_xsl = re.sub(
                pattern,
                lambda m, b=body: m.group(1) + "\n" + b + "   </xsl:template>",
                base_xsl)

        # --- helpers (z folderu helpers/ + domknięcie 'uses') ---
        required_helpers = self._collect_required_helpers()
        helpers_block = self._read_helpers_block(required_helpers)
        base_xsl = self._inject_helpers_into_xslt(base_xsl, helpers_block)

        # --- zmienne globalne (feed-scope): auto-wstrzyk referowanych, a niezadeklarowanych ---
        base_xsl = self._inject_globals(base_xsl)

        # --- opcjonalna zmiana prefiksu przestrzeni nazw (g: → …) ---
        base_xsl = self._apply_prefix_override(base_xsl)

        return base_xsl

    
    def _collect_required_helpers(self) -> List[str]:
        """Zbierz nazwy helperów z wybranych parametrów + domknięcie 'uses' z rejestru."""
        required: set = set()

        def add(h: str) -> None:
            if h in required:
                return
            required.add(h)
            for dep in self.helpers_registry.get(h, {}).get("uses", []):
                add(dep)

        for context, params in self.selected_params.items():
            for param_name in params:
                for h in self.parameters[param_name]['data'].get("helpers", []):
                    add(h)

        return sorted(required)

    def _read_helpers_block(self, required: List[str]) -> str:
        """Wczytaj potrzebne helpery jako gotowe pliki z folderu helpers/."""
        blocks = []
        for name in required:
            helper_file = self.helpers_path / f"{name}.xsl"
            if helper_file.exists():
                blocks.append(self._read_xslt_file(helper_file).strip())
            else:
                print(f"⚠️  Brak pliku helpera: {name}.xsl")
        return "\n\n".join(blocks)

    def _inject_globals(self, base_xsl: str) -> str:
        """Wstaw po <xsl:output> te zmienne globalne (scope=global z rejestru),
        które są referowane ($nazwa) w arkuszu, a nie są jeszcze zadeklarowane."""
        decls = []
        for name, meta in self.variables_registry.items():
            if meta.get("scope") != "global":
                continue
            referenced = re.search(r'\$' + re.escape(name) + r'\b', base_xsl)
            declared = re.search(
                r'<xsl:variable\s+name=["\']' + re.escape(name) + r'["\']', base_xsl)
            if referenced and not declared:
                global_file = self.variables_path / f"{name}.xsl"
                if global_file.exists():
                    decls.append("   " + self._read_xslt_file(global_file).strip())
                else:
                    print(f"⚠️  Brak pliku zmiennej globalnej: {name}.xsl")

        if not decls:
            return base_xsl

        block = "\n" + "\n".join(decls) + "\n"
        # callable — treść globali może mieć backslashe (np. corrected='\GRATIS\')
        return re.sub(r'(<xsl:output[^>]*/>)',
                      lambda m, b=block: m.group(1) + b, base_xsl, count=1)

    def _inject_helpers_into_xslt(self, xslt: str, helpers_block: str) -> str:
        """Wstaw helpers przed </xsl:stylesheet>."""
        if not helpers_block.strip():
            return xslt

        # callable — helpery (wordFormat, throwNode…) zawierają backslashe
        return re.sub(
            r'</xsl:stylesheet>',
            lambda m, b=helpers_block: b + "\n</xsl:stylesheet>",
            xslt,
            flags=re.DOTALL
        )



    def _save_output(self, xslt_content: str) -> bool:
        """Zapisz wygenerowany XSLT do pliku."""
        structure_name = self.selected_structure['data']['name']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{structure_name}_generated_{timestamp}.xsl"
        output_file = self.output_path / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xslt_content)
            
            print("\n" + self.t('saved', name=output_file.name))
            return True
        except IOError as e:
            print("\n" + self.t('save_error', e=e))
            return False
    
    def _show_summary(self) -> None:
        """Pokaż podsumowanie wyborów."""
        self._print_header(self.t('header_summary'))

        print(self.t('structure_label', name=self.selected_structure['data']['name']))
        print(f"   └─ {self._desc(self.selected_structure['data'])}\n")

        print(self.t('selected_params'))
        if self.selected_params:
            for context, params in sorted(self.selected_params.items()):
                print(f"\n   {context}:")
                for param in params:
                    default_out = self.parameters[param]['data'].get('output', '')
                    custom = self.output_overrides.get(param)
                    shown = f"{default_out} → {custom}" if custom else default_out
                    print(f"     • {param} - {shown}")
        else:
            print(self.t('no_selection'))

        print("\n" + "=" * 70)
        print("\n" + self.t('generating'))

        xslt_content = self._build_xslt_structure()
        success = self._save_output(xslt_content)

        if success:
            input("\n" + self.t('press_enter'))
    
    def run(self) -> None:
        """Główna pętla aplikacji."""
        # Krok 0: Wybór języka interfejsu
        if not self._choose_language():
            print("\n" + self.t('goodbye'))
            return

        while True:
            # Krok 1: Wybór struktury
            structure_name = self._show_structure_menu()
            if not structure_name:
                print("\n" + self.t('goodbye'))
                break

            self.selected_structure = self.structures[structure_name]

            # Krok 2: Filtrowanie parametrów
            available_params = self._filter_parameters_for_structure(structure_name)

            if not available_params:
                self._print_header(self.t('header_no_params'))
                print(self.t('no_params_for', name=structure_name))
                input("\n" + self.t('press_enter_back'))
                continue

            # Krok 3: Wybór parametrów
            self.selected_params = self._show_parameters_menu(available_params)

            # Krok 4: Opcjonalna zmiana nazw elementów wyjściowych
            self._ask_output_names(self.selected_params)

            # Krok 5: Podsumowanie i generowanie
            self._show_summary()

            # Reset dla następnego cyklu
            self.selected_structure = None
            self.selected_params = {}
            self.output_overrides = {}


def main():
    """Punkt wejścia aplikacji."""
    try:
        app = SummonFeedGenerator()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Przerwano przez użytkownika.")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
