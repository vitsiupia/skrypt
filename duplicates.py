import pandas as pd

def remove_duplicates(input_file1, input_file2, output_file):
    try:
        # Wczytaj dane z pierwszego pliku
        df1 = pd.read_excel(input_file1)

        # Wczytaj dane z drugiego pliku
        df2 = pd.read_excel(input_file2)

        # Połącz obie ramki danych
        combined_df = pd.concat([df1, df2])

        # Usuń duplikaty na podstawie wszystkich kolumn
        combined_df = combined_df.drop_duplicates()

        # Zapisz wynik do nowego pliku
        combined_df.to_excel(output_file, index=False)

        print(f"Usunięto duplikaty i zapisano wynik do {output_file}")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    input_file1 = 'offers2_0.xlsx'
    input_file2 = 'offers2_1.xlsx'
    output_file = 'wynik.xlsx'

    remove_duplicates(input_file1, input_file2, output_file)

