import pandas as pd
import os
import logging
from utils import assign_period, subscription_time, get_trend, get_range, check_if_returned

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_etl():
    logging.info("Uruchamianie Systemu ETL KajoDATA...")
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    
    RAW_PATH = os.path.join(PROJECT_ROOT, "Raw", "KDS Transactions.xlsx")
    MAP_PATH = os.path.join(SCRIPT_DIR, "price_mapping.csv")
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        logging.info(f"Wczytywanie danych surowych z {RAW_PATH}")
        df_raw = pd.read_excel(RAW_PATH, usecols=['Data transakcji', 'Klient', 'Kwota'])
    except Exception as e:
        logging.error(f"Błąd podczas wczytywania danych: {e}")
        return


    # CZYSZCZENIE I PRZYGOTOWANIE DANYCH WEJŚCIOWYCH
    df = df_raw.copy()
    df['Data transakcji'] = pd.to_datetime(df['Data transakcji'])
    df = df.dropna(subset=['Klient'])
    df = df.sort_values(['Klient', 'Data transakcji']).reset_index(drop=True)
    
    
    # MAPOWANIE CEN I ZASILANIE DANYCH
    if os.path.exists(MAP_PATH):
        logging.info("Aplikowanie mapowania cen...")
        price_map = pd.read_csv(MAP_PATH, sep=';', decimal=',', encoding='utf-8-sig')
        price_map = price_map.drop_duplicates(subset='Kwota')
        df = pd.merge(df, price_map, on='Kwota', how='left')
    else:
        logging.warning("Brak pliku price_mapping.csv!")

    
    # Tworzenie tabeli z metrykami klientów
    logging.info("Tworzenie metryki klientów...")

    df['Pierwsza płatność'] = df.groupby('Klient')['Data transakcji'].transform('min').dt.normalize()
    df['Ostatnia płatność'] = df.groupby('Klient')['Data transakcji'].transform('max').dt.normalize()
    df['Kohorta'] = df['Pierwsza płatność'].dt.to_period('M')
    df['Grupa Kohort'] = df['Pierwsza płatność'].apply(assign_period)
    df['Nr Transakcji'] = df.groupby('Klient').cumcount() + 1
    df['Ostatnia transakcja'] = (~df.duplicated(subset='Klient', keep='last')).astype(int)

    rank = df['Czas dostępu'].map({'Miesiąc': 1, 'Rok': 2, '2 Lata': 3})
    first_rank = rank.groupby(df['Klient']).transform('first')
    last_rank = rank.groupby(df['Klient']).transform('last')
    n_unique = rank.groupby(df['Klient']).transform('nunique')
    df['Zmiana planu'] = [get_trend(f, l, n) for f, l, n in zip(first_rank, last_rank, n_unique)]

    df['Koniec subskrypcji'] = df.apply(subscription_time, axis=1).dt.normalize()
    max_date = df['Data transakcji'].max()
    df['Status_Sub'] = df['Koniec subskrypcji'].apply(lambda x: 'Aktywny' if x >= max_date else 'Wygasły')
    df['LTV Narastajaco'] = df.groupby('Klient')['Kwota'].cumsum().round(2)
    df['Wiek_Msc'] = (df['Data transakcji'].dt.year - df['Pierwsza płatność'].dt.year) * 12 + (df['Data transakcji'].dt.month - df['Pierwsza płatność'].dt.month)

    client_metrics = df.groupby('Klient').agg({
        'Pierwsza płatność': 'first',
        'Ostatnia płatność': 'last',
        'Kohorta': 'first',
        'Grupa Kohort': 'first',
        'Czas dostępu': 'first',
        'Zmiana planu': 'first',
        'Status_Sub': 'last',
        'Kwota': 'sum'
    }).rename(columns={'Kwota': 'LTV_Total'})


    final_columns_main = ['Data transakcji', 'Klient', 'Kwota', 'Nr Transakcji', 'Wiek_Msc', 'LTV Narastajaco']
    df_output = df[final_columns_main]
    
    #eksport tabeli głównej
    clean_path = os.path.join(OUTPUT_DIR, "KDS_Cleaned_Transactions.csv")
    df_output.to_csv(clean_path, sep=';', index=False, encoding='utf-8-sig', decimal=',')
    logging.info(f"Wyeksportowano tabelę główną: {clean_path}")

    #tworzenie macierzy retencji
    logging.info("Tworzenie macierzy retencji...")
    matrix_df = df[['Klient']].assign(M=df.apply(get_range, axis=1)).explode('M')
    matrix = matrix_df.pivot_table(index='Klient', columns='M', aggfunc='size', fill_value=0)
    matrix = (matrix > 0).astype(int)
    current_month = df['Data transakcji'].max().to_period('M')
    matrix = matrix.loc[:, :current_month]
    
    matrix['Suma_Miesiecy'] = matrix.sum(axis=1)
    matrix['Wrocil'] = matrix.drop(columns=['Suma_Miesiecy']).apply(check_if_returned, axis=1)
    
    is_decimal = df.groupby('Klient')['Kwota'].apply(lambda x: any(v % 1 > 0.001 for v in x))
    matrix['Typ_Ceny'] = matrix.index.map(is_decimal).map({True: 'Promocyjna', False: 'Standardowa'})
    matrix['Staly_Klient'] = (matrix['Suma_Miesiecy'] >= 13).astype(int).map({1: 'Tak', 0: 'Nie'})
    matrix = matrix.join(client_metrics)
    
    cohort_data = matrix.copy()
    
    matrix['Kohorta'] = matrix['Kohorta'].dt.strftime('%m.%Y')
    

    # eksport macierzy retencji
    matrix_path = os.path.join(OUTPUT_DIR, "KDS_Matrix.csv")
    matrix.to_csv(matrix_path, sep=';', encoding='utf-8-sig', decimal=',')
    logging.info(f"Wyeksportowano pełną bazę klientów (Matrix): {matrix_path}")
    
    # Tworzenie tabeli retencji (format długi)
    logging.info("Generowanie docelowej tabeli retencji (format długi)...")
    
    metadata_cols = [
        'Klient', 'Kohorta', 'Grupa Kohort', 'Czas dostępu', 'Suma_Miesiecy', 
        'Wrocil', 'Pierwsza płatność', 'Ostatnia płatność', 'Zmiana planu', 
        'Status_Sub', 'LTV_Total', 'Typ_Ceny', 'Staly_Klient'
    ]

    long_retention = cohort_data.reset_index().melt(
        id_vars=metadata_cols, 
        var_name='Data_Miesiac', 
        value_name='Aktywny'
    )
    long_retention['Data_Miesiac'] = pd.PeriodIndex(long_retention['Data_Miesiac'], freq='M')
    long_retention['Miesiac_Relatywny'] = (long_retention['Data_Miesiac'] - long_retention['Kohorta']).apply(lambda x: x.n)
    long_retention = long_retention[long_retention['Miesiac_Relatywny'] >= 0]
    long_retention['Kohorta'] = long_retention['Kohorta'].dt.strftime('%m.%Y')
    

    # eksport tabeli retencji (format długi)
    long_path = os.path.join(OUTPUT_DIR, "KDS_Long_Retention.csv")
    long_retention.to_csv(long_path, sep=';', index=False, encoding='utf-8-sig', decimal=',')
    logging.info(f"Wyeksportowano tabelę retencji (Long): {long_path}")
    logging.info("Proces ETL zakończny pomyślnie!")

if __name__ == "__main__":
    run_etl()
