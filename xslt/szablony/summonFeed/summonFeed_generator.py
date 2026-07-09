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
        self.output_path = self.base_path

        self.structures: Dict = {}
        self.parameters: Dict = {}
        self.variables_registry: Dict = {}
        self.helpers_registry: Dict = {}
        self.selected_structure: Optional[Dict] = None
        self.selected_params: Dict[str, List[Dict]] = {}

        self._load_data()
    
    def _load_data(self) -> None:
        """Wczytaj wszystkie struktury i parametry JSON."""
        # Wczytaj struktury
        for json_file in self.structures_path.glob("*.json"):
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
    
    def _show_structure_menu(self) -> Optional[str]:
        """Pokaż menu wyboru struktury."""
        self._print_header("WYBÓR STRUKTURY FEEDU")
        
        structures_list = list(self.structures.keys())
        
        if not structures_list:
            print("❌ Nie znaleziono struktur!")
            return None
        
        for i, name in enumerate(structures_list, 1):
            desc = self.structures[name]['data'].get('description', '')
            print(f"{i}. {name}")
            print(f"   └─ {desc}")
            print()
        
        print("0. Wyjście")
        print()
        
        while True:
            try:
                choice = int(input("Wybierz numer: ").strip())
                if choice == 0:
                    return None
                if 1 <= choice <= len(structures_list):
                    return structures_list[choice - 1]
                print("❌ Nieprawidłowy wybór!")
            except ValueError:
                print("❌ Wpisz prawidłowy numer!")
    
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
        self._print_header("WYBÓR PARAMETRÓW")
        
        selected = {}
        
        for context, param_names in sorted(available_params.items()):
            print(f"\n📦 Kontekst: {context}")
            print("-" * 70)
            
            # Wyświetl dostępne parametry
            for i, param_name in enumerate(param_names, 1):
                param_data = self.parameters[param_name]['data']
                desc = param_data.get('description', '')
                print(f"{i}. {param_name}: {desc}")
            
            print()
            print("Wpisz numery oddzielone spacjami (np: 1 2 3) lub Enter aby pominąć")
            
            while True:
                try:
                    user_input = input(f"Wybór dla '{context}': ").strip()
                    
                    if not user_input:  # Pomiń ten kontekst
                        break
                    
                    choices = [int(x.strip()) for x in user_input.split()]
                    
                    # Waliduj wybory
                    if all(1 <= c <= len(param_names) for c in choices):
                        selected[context] = [param_names[c - 1] for c in choices]
                        break
                    else:
                        print("❌ Jeden z numerów jest poza zakresem!")
                except ValueError:
                    print("❌ Wpisz prawidłowe numery!")
        
        return selected
    
    def _read_xslt_file(self, xsl_path: Path) -> str:
        """Wczytaj zawartość pliku XSLT."""
        try:
            with open(xsl_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Nie znaleziono pliku: {xsl_path}")
            return ""
    
    # ---------------------------------------------------------
    #  OBSŁUGA CONFIGVARS
    # ---------------------------------------------------------

    def _get_config_vars(self, param_name: str) -> List[Dict]:
        return self.parameters[param_name]['data'].get('configVars', [])

    def _format_config_value(self, raw_value: str, delimeter: str) -> str:
        """Formatuje wartość configVar zgodnie z separatorem."""
        raw_value = raw_value.strip()
      
        # brak separatora → zwróć jak jest
        if not delimeter:
            return raw_value
      
        # rozbij po spacjach
        parts = [p.strip() for p in raw_value.split() if p.strip()]
      
        # jeśli tylko jeden element → otocz separatorem
        if len(parts) == 1:
            return f"{delimeter}{parts[0]}{delimeter}"
      
        # wiele elementów → separator między nimi
        return delimeter + delimeter.join(parts) + delimeter

    def _ask_for_config_vars(self, config_vars: List[Dict]) -> Dict[str, str]:
        values = {}
        if not config_vars:
            return values

        print("\n🔧 Parametr wymaga dodatkowych ustawień (configVars):\n")

        for var in config_vars:
            name = var['name']
            default = var.get('default', '')
            delimeter = var.get('delimeter', '')

            prompt = f"Podaj wartość dla {name} (domyślnie '{default}'): "
            user_input = input(prompt).strip()

            # jeśli użytkownik nic nie podał → użyj domyślnej
            raw_value = user_input if user_input else default

            # sformatuj zgodnie z separatorem
            formatted = self._format_config_value(raw_value, delimeter)

            values[name] = formatted

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
        user_input = input(f"Podaj wartość dla {name} (domyślnie '{default}'): ").strip()
        raw_value = user_input if user_input else default
        return self._format_config_value(raw_value, delimeter)

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
            
            print(f"\n✅ Plik zapisany: {output_file.name}")
            return True
        except IOError as e:
            print(f"\n❌ Błąd przy zapisie pliku: {e}")
            return False
    
    def _show_summary(self) -> None:
        """Pokaż podsumowanie wyborów."""
        self._print_header("PODSUMOWANIE")
        
        print(f"📦 Struktura: {self.selected_structure['data']['name']}")
        print(f"   └─ {self.selected_structure['data'].get('description', '')}\n")
        
        print("📝 Wybrane parametry:")
        if self.selected_params:
            for context, params in sorted(self.selected_params.items()):
                print(f"\n   {context}:")
                for param in params:
                    param_data = self.parameters[param]['data']
                    print(f"     • {param} - {param_data.get('output', '')}")
        else:
            print("   (brak wyboru)")
        
        print("\n" + "=" * 70)
        print("\nGenerowanie XSLT...")
        
        xslt_content = self._build_xslt_structure()
        success = self._save_output(xslt_content)
        
        if success:
            input("\nNaciśnij Enter aby kontynuować...")
    
    def run(self) -> None:
        """Główna pętla aplikacji."""
        while True:
            # Krok 1: Wybór struktury
            structure_name = self._show_structure_menu()
            if not structure_name:
                print("\n👋 Do widzenia!")
                break
            
            self.selected_structure = self.structures[structure_name]
            
            # Krok 2: Filtrowanie parametrów
            available_params = self._filter_parameters_for_structure(structure_name)
            
            if not available_params:
                self._print_header("BRAK PARAMETRÓW")
                print(f"Dla struktury '{structure_name}' brak dostępnych parametrów.")
                input("\nNaciśnij Enter aby wrócić...")
                continue
            
            # Krok 3: Wybór parametrów
            self.selected_params = self._show_parameters_menu(available_params)
            
            # Krok 4: Podsumowanie i generowanie
            self._show_summary()
            
            # Reset dla następnego cyklu
            self.selected_structure = None
            self.selected_params = {}


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
