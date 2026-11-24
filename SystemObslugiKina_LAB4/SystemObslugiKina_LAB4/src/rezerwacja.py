from .miejsce import Miejsce
from .seans import Seans


class Rezerwacja:

    def __init__(self, id: int, seans: Seans, miejsca: list[Miejsce]):
        self.id = id
        self.seans = seans
        self.miejsca = miejsca.copy()
        self.status = "aktywna"
        self.statusPlatnosci = "nieoplacona"
        self.cenaCalkowita = self.obliczCene()

    def obliczCene(self) -> float:
        return len(self.miejsca) * self.seans.cenaBiletu

    def anuluj(self) -> None:
        if self.status == "anulowana":
            raise ValueError("Rezerwacja została już anulowana.")
        if self.statusPlatnosci == "oplacona":
            raise ValueError("Nie można anulować opłaconej rezerwacji bez obsługi zwrotu.")
        self.status = "anulowana"

    def oplac(self) -> None:
        if self.status != "aktywna":
            raise ValueError("Nie można opłacić anulowanej rezerwacji.")
        if self.statusPlatnosci == "oplacona":
            raise ValueError("Rezerwacja jest już opłacona.")
        self.statusPlatnosci = "oplacona"
