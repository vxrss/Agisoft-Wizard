# Agisoft Wizard
Autor: Stanisław Trocyk

Skrypt w języku Python automatyzujący pełny proces przetwarzania fotogrametrycznego w programie Agisoft Metashape.

## Główne funkcje:
* **Interfejs GUI**: Pozwala na wybór zdjęć, pliku osnowy (.txt) i zdefiniowanie układów współrzędnych (CRS kamer, CRS osnowy, CRS wynikowy projektu).
* **Orientacja zdjęć (SfM)**: Automatyczne wczytanie zdjęć i wyznaczenie położenia kamer.
* **Inteligentne dopasowanie osnowy**: Algorytm wykrywa niekodowane znaczniki krzyżowe i łączy je przestrzennie  ze wczytanymi współrzędnymi referencyjnymi. 
* **Optymalizacja**: Samoczynne przeliczenie orientacji przy użyciu prawidłowo dopasowanych fotopunktów.
* **Modelowanie 3D**: Generowanie gęstej chmury punktów oraz oteksturowanego modelu 3D.
* **Eksport EO**: Zapis elementów orientacji zewnętrznej kamer powiązanych ze zdjęciami do pliku `EO.txt`.

## Sposób użycia:
1. Otwórz program Agisoft Metashape.
2. Z górnego menu wybierz `Tools -> Run Script...` i wskaż plik `main.py`.
3. Na głównym pasku menu Agisoft pojawi się zakładka **Wizard**, kliknij **Wizard** aby otworzyć okno konfiguracji.
