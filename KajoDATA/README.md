# KajoDATA - Automatyczny System Analizy 🚀

Projekt stworzony na potrzeby konkursu **KajoDATA**. Jego głównym celem jest zrozumienie, jak ceny i promocje wpływają na to, czy klienci z nami zostają, czy odchodzą.

## 📉 Kluczowe Wnioski Biznesowe
1.  **Promocje realnie budują lojalność**: Klienci, którzy dołączyli w cenie promocyjnej, mają **o 15-20% wyższą retencję** po pierwszym roku niż ci w cenie standardowej.
2.  **Wyższy LTV mimo niższej ceny**: Choć klienci promocyjni płacą mniej miesięcznie, to przez to, że zostają z nami znacznie dłużej, sumarycznie przynoszą **wyższy średni przychód (LTV)**.
3.  **Klienci roczni są "jednorazowi"**: Bardzo rzadko przedłużają subskrypcję lub zmieniają model po roku. Choć krótkoterminowo są zyskowni (płacą z góry), długofalowo nie budują stałej bazy – aż **86 na 93 osoby**, które powróciły do serwisu, zaczynało od planu miesięcznego.
4.  **Potencjał w reaktywacjach**: Obecnie tylko ok. 8% użytkowników wraca po wygaśnięciu subskrypcji. Uruchomienie kampanii win-back mogłoby znacząco zwiększyć przychody niskim kosztem.
5.  **Psychologiczne granice cenowe**: Dane sugerują istnienie wyraźnych progów, powyżej których zainteresowanie zakupem spada – jest to ok. **200 PLN** dla subskrypcji miesięcznej oraz **1300-1400 PLN** dla rocznej.

## 💡 Idea projektu: "Hybryda"
Zamiast robić wszystko w jednym narzędziu, stworzyłem system łączący siłę programowania z wygodą Excela:
1.  **Python ("Maszyna")**: Wykonuje całą "brudną robotę" – czyści dane, łączy tabele i wykonuje trudne obliczenia matematyczne.
2.  **Excel ("Centrum Dowodzenia")**: Służy do przeglądania gotowych wyników, filtrowania ich i wyciągania wniosków biznesowych przez Power Query.

---

## ⚠️ Nota o danych
Analiza została przeprowadzona na podstawie dostępnego wycinka danych transakcyjnych. Architektura systemu jest jednak elastyczna – w przypadku uzyskania dostępu do pełniejszych rekordów (np. precyzyjnych dat obowiązywania promocji), można łatwo zaktualizować założenia w pliku `price_mapping.csv`. Cała analityka i wizualizacje odświeżą się wtedy automatycznie.

---

## 🛠️ Jak to działa? (Flow danych)

Proces jest w pełni zautomatyzowany i wygląda następująco:

`DANE RAW (Excel)` ➡️ `MASZYNA (Python)` ➡️ `PLIKI PRZEJŚCIOWE (CSV)` ➡️ `DASHBOARD (Excel + Power Query)`

1.  **Dane Raw**: Wrzucasz surowy wyciąg z transakcji do folderu `Raw`.
2.  **Maszyna (Python)**: Uruchamiasz skrypt, który:
    *   Naprawia błędy w datach i brakujące dane.
    *   Przypisuje ceny do konkretnych planów (miesięczny, roczny itp.).
    *   Liczy **Retencję** (czyli kto i na jak długo z nami zostaje).
    *   Generuje **Krzywą Przeżywalności** (porównanie standardowych cen i promocji).
3.  **Power Query**: Excel sam "zasysa" przetworzone dane z plików CSV.
4.  **Dashboard**: Otrzymujesz gotowe wykresy i tabele, które odświeżają się jednym kliknięciem.

---

## 📂 Struktura Projektu

```text
KajoDATA/
├── Dashboard/           # Raport Excel i wizualizacje
├── Kod/                 # Silnik Python:
│   ├── ETL_System.py        # Skrypt do automatyzacji procesu
│   ├── KDS_ETL_Analysis.ipynb # Proces analizy krok po kroku + wizualizacje
│   ├── utils.py             # Funkcje logiczne i pomocnicze
│   └── price_mapping.csv    # Słownik cen i produktów
├── Output/              # Gotowe dane CSV (wsad do Excela)
├── Raw/                 # Miejsce na surowe pliki .xlsx
├── README.md            # Dokumentacja projektu
└── requirements.txt     # Lista bibliotek do zainstalowania
```

---

## 📖 Słownik Pojęć

| Pojęcie | Definicja |
| :--- | :--- |
| **Kohorta** | Grupa klientów, którzy rozpoczęli subskrypcję w tym samym miesiącu. Pozwala śledzić zachowanie konkretnych "fal" użytkowników. |
| **Retencja** | Wskaźnik utrzymania klienta. Informuje, jaki procent kohorty wciąż płaci po X miesiącach. |
| **Churn (Odejścia)** | Przeciwieństwo retencji – procent klientów, którzy zrezygnowali z usługi. |
| **LTV (Lifetime Value)** | Całkowity przychód, jaki generuje klient w całym okresie swojej "znajomości" z firmą. |
| **Staż (Tenure)** | Czas (liczba miesięcy), przez który klient pozostaje aktywny w systemie. |
| **Survival Analysis** | Statystyczna analiza "przeżywalności" klientów, użyta do porównania grup cenowych (Standard vs Promo). |
| **Upgrade / Downgrade** | Zmiana planu na droższy (np. z miesiąca na rok) lub tańszy. |
| **Typ Ceny** | Klasyfikacja transakcji. System automatycznie rozpoznaje cenę jako **Promocyjną**, jeśli kwota posiada części ułamkowe (grosze), co w tym zbiorze danych oznacza zastosowanie rabatu. |

---

## 🛠️ Wymagania i Instalacja

Aby uruchomić system "Maszyny" (Python), musisz mieć zainstalowane następujące biblioteki:
*   **pandas** i **openpyxl** (do obsługi danych i plików Excel)
*   **matplotlib** i **seaborn** (do generowania wykresów)
*   **numpy** (do obliczeń macierzowych)

Najszybciej zainstalujesz je wszystkie jedną komendą:
```bash
pip install -r requirements.txt
```

---

## 🚀 Instrukcja "Na Skróty"

1.  Upewnij się, że masz zainstalowane wymagane biblioteki (punkt wyżej).
2.  Wklej plik `KDS Transactions.xlsx` do folderu `/Raw`.
3.  Otwórz i uruchom `Kod/KDS_ETL_Analysis.ipynb` (lub uruchom `ETL_System.py`).
4.  Otwórz plik w folderze `/Dashboard` i kliknij **Dane -> Odśwież wszystko**.
5.  Gotowe! Analiza jest aktualna.

---
