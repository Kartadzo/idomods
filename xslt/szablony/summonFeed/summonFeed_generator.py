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
        self.output_path = self.base_path
        
        self.structures: Dict = {}
        self.parameters: Dict = {}
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
            xslt = re.sub(pattern, replacement, xslt, flags=re.DOTALL)
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
    
    def _build_xslt_structure(self) -> str:
        """Zbuduj ostateczny plik XSLT."""
        structure_data = self.selected_structure['data']
        base_xsl = self._read_xslt_file(self.selected_structure['xsl_path'])
        
        # Znajdź i wypełnij każdy insertion point
        for insertion_point in structure_data.get('insertionPoints', []):
            template_name = insertion_point['template']
            context = insertion_point['context']
            
            # Zbierz kod dla tego kontekstu
            template_body = ""
            if context in self.selected_params:
                for param_name in self.selected_params[context]:
                    param_content = self._get_template_content(param_name)
                    template_body += f"      <!-- {param_name} -->\n"
                    template_body += f"      {param_content}\n"
            
            # Wymień pusty template na wypełniony
            pattern = f'<xsl:template name="{template_name}"[^>]*>\\s*</xsl:template>'
            replacement = f'''<xsl:template name="{template_name}" \\
                 xmlns:g="http://base.google.com/ns/1.0">
{template_body}   </xsl:template>'''
            
            base_xsl = re.sub(pattern, replacement, base_xsl)
        
        return base_xsl
    
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
