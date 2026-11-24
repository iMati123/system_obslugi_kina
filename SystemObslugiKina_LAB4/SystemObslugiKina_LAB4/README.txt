SYSTEM OBSLUGI KINA — PROJEKT NA LAB 4
=====================================

Jak uruchomic w PyCharm:
1. Rozpakuj plik ZIP.
2. W PyCharm wybierz File > Open i wskaz folder SystemObslugiKina_LAB4.
3. Wybierz interpreter Python 3.10 lub nowszy (bez dodatkowych bibliotek).
4. Kliknij prawym przyciskiem myszy plik main.py > Run 'main'.
5. W konsoli pojawi sie przykladowa rezerwacja, wykrycie zajetego miejsca i anulowanie.

Struktura:
- main.py                 przyklad uzycia wszystkich potrzebnych obiektow
- src/film.py             klasa Film
- src/sala.py             klasa Sala
- src/miejsce.py          klasa Miejsce
- src/seans.py            klasa Seans
- src/rezerwacja.py       klasa Rezerwacja
- src/system_kina.py      klasa SystemKina

Zgodnosc z UML:
- Film 1 -- 0..* Seans: Seans ma pole film i film_id.
- Sala 1 -- 0..* Seans: Seans ma pole sala.
- Sala 1 -- 1..* Miejsce: Sala tworzy liste obiektow Miejsce.
- Seans 1 -- 0..* Rezerwacja: Seans przechowuje swoje rezerwacje.
- Rezerwacja 0..* -- 1..* Miejsce: Rezerwacja przechowuje wybrane miejsca.
- SystemKina przechowuje listy seansow i rezerwacji.

Drobne szczegoly implementacji:
- Konstruktor Seans przyjmuje obiekt Film, z ktorego uzyskuje film_id.
- Film.pobierzOpis() buduje opis na podstawie tytulu, gatunku i czasu trwania,
  poniewaz osobnego pola 'opis' nie ma na diagramie UML.
- Pola film, sala, miejsca i rezerwacje reprezentuja relacje UML i dlatego
  pojawiaja sie w kodzie, nawet gdy nie sa rozpisane w sekcjach atrybutow UML.
- PobierzWolneMiejsca sprawdza aktywne rezerwacje dla konkretnego seansu.
- Oplac() zmienia jedynie status platnosci. Nie jest to obsluga prawdziwych platnosci.
- Nie ma jeszcze interfejsu graficznego, pliku .exe ani bazy danych. Na LAB 4
  wymagany jest model klas i dzialajaca logika w main.py.
