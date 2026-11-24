
"""LAB 7: uruchomienie okna aplikacji Tkinter zamiast menu konsolowego."""

from datetime import datetime, timedelta
import tkinter as tk

from src.baza_danych import BazaDanych
from src.film import Film
from src.sala import Sala
from src.seans import Seans
from src.system_kina import SystemKina
from src.gui import AplikacjaKina


def dodajPrzykladoweDane(system: SystemKina) -> None:
    """Dodaj seans demonstracyjny tylko do pustej bazy."""
    if system.przegladajSeanse():
        return

    film = Film(1, "Interstellar", 169, "science fiction")
    sala = Sala(1, "Sala niebieska", liczbaRzedow=2, miejscWRzedzie=4)
    termin = (datetime.now() + timedelta(days=3)).replace(
        hour=18, minute=0, second=0, microsecond=0
    )
    system.dodajSeans(Seans(10, termin, film, sala, 30.0))


def main() -> None:
    baza = BazaDanych()
    system = SystemKina(baza)
    dodajPrzykladoweDane(system)

    okno = tk.Tk()
    AplikacjaKina(okno, system)
    okno.mainloop()


if __name__ == "__main__":
    main()

