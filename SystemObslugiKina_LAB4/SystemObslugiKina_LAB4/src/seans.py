from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .film import Film
from .sala import Sala

if TYPE_CHECKING:
    from .miejsce import Miejsce
    from .rezerwacja import Rezerwacja


class Seans:
    """Konkretny pokaz filmu w określonej sali i terminie."""

    def __init__(self, id: int, dataGodzina: datetime, film: Film,
                 sala: Sala, cenaBiletu: float):
        if cenaBiletu < 0:
            raise ValueError("Cena biletu nie może być ujemna.")

        self.id = id
        self.dataGodzina = dataGodzina
        self.film_id = film.film_id  # Pole z diagramu UML.
        self.cenaBiletu = cenaBiletu
        self.film = film              # Asocjacja Film — Seans.
        self.sala = sala              # Asocjacja Sala — Seans.
        self.rezerwacje: list[Rezerwacja] = []  # Asocjacja Seans — Rezerwacja.

    def ustawCene(self, cena: float) -> None:
        if cena < 0:
            raise ValueError("Cena biletu nie może być ujemna.")
        self.cenaBiletu = cena

    def pobierzWolneMiejsca(self) -> list[Miejsce]:
        # Miejsce jest zajęte tylko wtedy, gdy istnieje aktywna
        # rezerwacja tego miejsca NA TEN KONKRETNY seans.
        zajete = {
            miejsce
            for rezerwacja in self.rezerwacje
            if rezerwacja.status == "aktywna"
            for miejsce in rezerwacja.miejsca
        }
        return [m for m in self.sala.pobierzMiejsca() if m not in zajete]
