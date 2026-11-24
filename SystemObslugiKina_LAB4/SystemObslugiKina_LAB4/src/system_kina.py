
from __future__ import annotations

from typing import TYPE_CHECKING

from .miejsce import Miejsce
from .rezerwacja import Rezerwacja
from .seans import Seans

if TYPE_CHECKING:
    from .baza_danych import BazaDanych


class SystemKina:
    def __init__(self, baza: BazaDanych | None = None):
        self.baza = baza
        self.seanse: list[Seans] = []
        self.rezerwacje: list[Rezerwacja] = []

        if self.baza is not None:
            self.seanse, self.rezerwacje = self.baza.wczytajDane()

    def przegladajSeanse(self) -> list[Seans]:
        return self.seanse.copy()

    def _znajdzSeans(self, seansId: int) -> Seans:
        for seans in self.seanse:
            if seans.id == seansId:
                return seans

        raise ValueError(
            f"Nie znaleziono seansu o ID {seansId}."
        )

    def sprawdzDostepnosc(self, seansId: int) -> list[Miejsce]:
        seans = self._znajdzSeans(seansId)
        return seans.pobierzWolneMiejsca()

    def rezerwujMiejsca(
        self,
        seansId: int,
        miejsca: list[Miejsce]
    ) -> Rezerwacja:
        seans = self._znajdzSeans(seansId)

        if not miejsca:
            raise ValueError("Wybierz przynajmniej jedno miejsce.")

        if len(set(miejsca)) != len(miejsca):
            raise ValueError(
                "Nie można wybrać tego samego miejsca dwa razy."
            )

        if any(
            m not in seans.sala.pobierzMiejsca()
            for m in miejsca
        ):
            raise ValueError(
                "Wybrane miejsce nie należy do sali."
            )

        if any(
            m not in seans.pobierzWolneMiejsca()
            for m in miejsca
        ):
            raise ValueError(
                "Przynajmniej jedno miejsce jest już zajęte."
            )

        if self.baza is not None:
            rezerwacja = Rezerwacja(-1, seans, miejsca)
            rezerwacja.id = self.baza.zapiszRezerwacje(rezerwacja)
        else:
            nowe_id = max(
                (r.id for r in self.rezerwacje),
                default=0
            ) + 1

            rezerwacja = Rezerwacja(nowe_id, seans, miejsca)

        self.rezerwacje.append(rezerwacja)
        seans.rezerwacje.append(rezerwacja)

        return rezerwacja

    def _znajdzRezerwacje(self, id: int) -> Rezerwacja:
        for rezerwacja in self.rezerwacje:
            if rezerwacja.id == id:
                return rezerwacja

        raise ValueError(
            f"Nie znaleziono rezerwacji o ID {id}."
        )

    def anulujRezerwacje(self, id: int) -> None:
        rezerwacja = self._znajdzRezerwacje(id)

        if rezerwacja.status == "anulowana":
            raise ValueError(
                "Rezerwacja została już anulowana."
            )

        if rezerwacja.statusPlatnosci == "oplacona":
            raise ValueError(
                "Nie można anulować opłaconej rezerwacji."
            )

        if self.baza is not None:
            self.baza.anulujRezerwacje(id)

        rezerwacja.anuluj()

    def oplacRezerwacje(self, id: int) -> None:
        rezerwacja = self._znajdzRezerwacje(id)

        if (
            rezerwacja.status != "aktywna"
            or rezerwacja.statusPlatnosci == "oplacona"
        ):
            raise ValueError(
                "Tej rezerwacji nie można opłacić."
            )

        if self.baza is not None:
            self.baza.oplacRezerwacje(id)

        rezerwacja.oplac()

    def dodajSeans(self, seans: Seans) -> None:
        if any(s.id == seans.id for s in self.seanse):
            raise ValueError(
                "Seans o takim ID już istnieje."
            )

        if self.baza is not None:
            self.baza.zapiszSeans(seans)

        self.seanse.append(seans)

    def usunSeans(self, id: int) -> None:
        seans = self._znajdzSeans(id)

        if any(
            r.status == "aktywna"
            for r in seans.rezerwacje
        ):
            raise ValueError(
                "Nie można usunąć seansu z aktywnymi rezerwacjami."
            )

        if self.baza is not None:
            self.baza.usunSeans(id)

        self.rezerwacje = [
            r for r in self.rezerwacje
            if r.seans is not seans
        ]
        self.seanse.remove(seans)

    def zmienCene(self, seansId: int, cena: float) -> None:
        seans = self._znajdzSeans(seansId)

        if cena < 0:
            raise ValueError(
                "Cena biletu nie może być ujemna."
            )

        if self.baza is not None:
            self.baza.zmienCene(seansId, cena)

        seans.ustawCene(cena)
