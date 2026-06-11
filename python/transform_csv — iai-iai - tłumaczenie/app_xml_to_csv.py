import os
import pandas as pd
import re

def load_two_csv_files(folder="."):
    csv_files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
    if len(csv_files) != 2:
        raise Exception("Folder musi zawierać dokładnie 2 pliki CSV.")
    file1, file2 = csv_files
    return pd.read_csv(file1), pd.read_csv(file2), file1, file2


def detect_language_columns(df):
    # znajdź kolumny name(lang)
    lang_cols = [c for c in df.columns if re.match(r"name\(.+\)", c)]
    if len(lang_cols) != 2:
        raise Exception("Plik musi zawierać dokładnie 2 kolumny name(lang).")
    return lang_cols


def detect_translation_source(df1, df2, lang_cols):
    lang1, lang2 = lang_cols

    # liczymy ile wierszy ma prawdziwe tłumaczenie (różne wartości)
    diff1 = (df1[lang1] != df1[lang2]).sum()
    diff2 = (df2[lang1] != df2[lang2]).sum()

    if diff1 > diff2:
        return df1, df2
    else:
        return df2, df1


def apply_translations(source, target, lang_cols):
    lang1, lang2 = lang_cols

    # mapa tłumaczeń tylko tam, gdzie wartości są różne
    translation_map = (
        source[source[lang1] != source[lang2]]
        .set_index(lang1)[lang2]
        .to_dict()
    )

    # maska: w target tłumaczymy tylko tam, gdzie lang2 == lang1
    untranslated_mask = target[lang1] == target[lang2]

    def translate(row):
        if not untranslated_mask.loc[row.name]:
            return row[lang2]  # już przetłumaczone
        return translation_map.get(row[lang1], row[lang2])

    target[lang2] = target.apply(translate, axis=1)
    return target


def main():
    df1, df2, file1, file2 = load_two_csv_files()

    # wykryj języki na podstawie jednego pliku
    lang_cols = detect_language_columns(df1)

    source, target = detect_translation_source(df1, df2, lang_cols)

    result = apply_translations(source, target, lang_cols)

    output_name = "uzupelnione_tlumaczenia.csv"
    result.to_csv(output_name, index=False, encoding="utf-8-sig")

    print(f"Gotowe! Wynik zapisany jako: {output_name}")


if __name__ == "__main__":
    main()
