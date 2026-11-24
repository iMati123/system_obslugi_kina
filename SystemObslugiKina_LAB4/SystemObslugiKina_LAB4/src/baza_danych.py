
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .film import Film
from .sala import Sala
from .seans import Seans
from .rezerwacja import Rezerwacja


class BazaDanych:
    def __init__(self, sciezka: str | Path | None = None):
        katalog = Path(__file__).resolve().parent.parent

        self.sciezka = (
            Path(sciezka)
            if sciezka is not None
            else katalog / "database" / "kino.db"
        )

        self.sciezka.parent.mkdir(parents=True, exist_ok=True)
        self.schemat = katalog / "database" / "schema.sql"

        with self._polaczenie() as db:
            db.executescript(
                self.schemat.read_text(encoding="utf-8")
            )

    @contextmanager
    def _polaczenie(self):
        db = sqlite3.connect(self.sciezka, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")

        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def zapiszSeans(self, seans: Seans) -> None:
        film = seans.film
        sala = seans.sala
        miejsca = sala.pobierzMiejsca()

        rzedow = max(m.rzad for m in miejsca)
        w_rzedzie = max(m.numer for m in miejsca)

        with self._polaczenie() as db:
            db.execute(
                "INSERT OR IGNORE INTO filmy "
                "(film_id, tytul, czas_trwania, gatunek) "
                "VALUES (?, ?, ?, ?)",
                (
                    film.film_id,
                    film.tytul,
                    film.czasTrwania,
                    film.gatunek
                )
            )

            istniejaca = db.execute(
                "SELECT liczba_rzedow, miejsc_w_rzedzie "
                "FROM sale WHERE sala_id = ?",
                (sala.numer,)
            ).fetchone()

            if istniejaca is not None and (
                istniejaca["liczba_rzedow"] != rzedow
                or istniejaca["miejsc_w_rzedzie"] != w_rzedzie
            ):
                raise ValueError(
                    "Sala o tym numerze ma inny układ miejsc."
                )

            db.execute(
                "INSERT OR IGNORE INTO sale "
                "(sala_id, nazwa, liczba_rzedow, miejsc_w_rzedzie) "
                "VALUES (?, ?, ?, ?)",
                (sala.numer, sala.nazwa, rzedow, w_rzedzie)
            )

            for miejsce in miejsca:
                db.execute(
                    "INSERT OR IGNORE INTO miejsca "
                    "(sala_id, rzad, numer) VALUES (?, ?, ?)",
                    (sala.numer, miejsce.rzad, miejsce.numer)
                )

            db.execute(
                "INSERT INTO seanse "
                "(seans_id, film_id, sala_id, "
                "data_godzina, cena_biletu) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    seans.id,
                    film.film_id,
                    sala.numer,
                    seans.dataGodzina.isoformat(timespec="minutes"),
                    seans.cenaBiletu
                )
            )

    def zapiszRezerwacje(self, rezerwacja: Rezerwacja) -> int:
        seans = rezerwacja.seans

        with self._polaczenie() as db:
            db.execute("BEGIN IMMEDIATE")
            ids_miejsc = []

            for miejsce in rezerwacja.miejsca:
                rekord = db.execute(
                    "SELECT miejsce_id FROM miejsca "
                    "WHERE sala_id = ? AND rzad = ? AND numer = ?",
                    (
                        seans.sala.numer,
                        miejsce.rzad,
                        miejsce.numer
                    )
                ).fetchone()

                if rekord is None:
                    raise ValueError(
                        "Nie znaleziono wskazanego miejsca."
                    )

                miejsce_id = rekord["miejsce_id"]

                zajete = db.execute(
                    "SELECT 1 FROM rezerwacja_miejsca rm "
                    "JOIN rezerwacje r "
                    "ON r.rezerwacja_id = rm.rezerwacja_id "
                    "WHERE r.seans_id = ? "
                    "AND r.status = 'aktywna' "
                    "AND rm.miejsce_id = ? LIMIT 1",
                    (seans.id, miejsce_id)
                ).fetchone()

                if zajete:
                    raise ValueError(
                        "Przynajmniej jedno miejsce jest już zajęte."
                    )

                ids_miejsc.append(miejsce_id)

            kursor = db.execute(
                "INSERT INTO rezerwacje "
                "(seans_id, status, status_platnosci, "
                "cena_calkowita) VALUES (?, ?, ?, ?)",
                (
                    seans.id,
                    rezerwacja.status,
                    rezerwacja.statusPlatnosci,
                    rezerwacja.cenaCalkowita
                )
            )

            nowe_id = kursor.lastrowid

            db.executemany(
                "INSERT INTO rezerwacja_miejsca "
                "(rezerwacja_id, miejsce_id) VALUES (?, ?)",
                [
                    (nowe_id, miejsce_id)
                    for miejsce_id in ids_miejsc
                ]
            )

        return nowe_id

    def anulujRezerwacje(self, rezerwacja_id: int) -> None:
        with self._polaczenie() as db:
            kursor = db.execute(
                "UPDATE rezerwacje SET status = 'anulowana' "
                "WHERE rezerwacja_id = ? "
                "AND status = 'aktywna' "
                "AND status_platnosci = 'nieoplacona'",
                (rezerwacja_id,)
            )

            if kursor.rowcount != 1:
                raise ValueError(
                    "Nie można anulować tej rezerwacji."
                )

    def oplacRezerwacje(self, rezerwacja_id: int) -> None:
        with self._polaczenie() as db:
            kursor = db.execute(
                "UPDATE rezerwacje "
                "SET status_platnosci = 'oplacona' "
                "WHERE rezerwacja_id = ? "
                "AND status = 'aktywna' "
                "AND status_platnosci = 'nieoplacona'",
                (rezerwacja_id,)
            )

            if kursor.rowcount != 1:
                raise ValueError(
                    "Nie można opłacić tej rezerwacji."
                )

    def zmienCene(self, seans_id: int, cena: float) -> None:
        if cena < 0:
            raise ValueError("Cena nie może być ujemna.")

        with self._polaczenie() as db:
            db.execute(
                "UPDATE seanse SET cena_biletu = ? "
                "WHERE seans_id = ?",
                (cena, seans_id)
            )

    def usunSeans(self, seans_id: int) -> None:
        with self._polaczenie() as db:
            kursor = db.execute(
                "DELETE FROM seanse WHERE seans_id = ?",
                (seans_id,)
            )

            if kursor.rowcount != 1:
                raise ValueError(
                    "Nie znaleziono seansu w bazie."
                )

    def wczytajDane(self) -> tuple[list[Seans], list[Rezerwacja]]:
        with self._polaczenie() as db:
            filmy = {
                row["film_id"]: Film(
                    row["film_id"],
                    row["tytul"],
                    row["czas_trwania"],
                    row["gatunek"]
                )
                for row in db.execute("SELECT * FROM filmy")
            }

            sale = {
                row["sala_id"]: Sala(
                    row["sala_id"],
                    row["nazwa"],
                    row["liczba_rzedow"],
                    row["miejsc_w_rzedzie"]
                )
                for row in db.execute("SELECT * FROM sale")
            }

            seanse = {}

            for row in db.execute(
                "SELECT * FROM seanse ORDER BY seans_id"
            ):
                seans = Seans(
                    row["seans_id"],
                    datetime.fromisoformat(row["data_godzina"]),
                    filmy[row["film_id"]],
                    sale[row["sala_id"]],
                    row["cena_biletu"]
                )
                seanse[seans.id] = seans

            rezerwacje = []

            for row in db.execute(
                "SELECT * FROM rezerwacje "
                "ORDER BY rezerwacja_id"
            ):
                seans = seanse[row["seans_id"]]
                wybrane_miejsca = []

                for wiersz in db.execute(
                    "SELECT m.rzad, m.numer "
                    "FROM rezerwacja_miejsca rm "
                    "JOIN miejsca m "
                    "ON m.miejsce_id = rm.miejsce_id "
                    "WHERE rm.rezerwacja_id = ? "
                    "ORDER BY m.rzad, m.numer",
                    (row["rezerwacja_id"],)
                ):
                    miejsce = next(
                        (
                            m for m in seans.sala.pobierzMiejsca()
                            if m.rzad == wiersz["rzad"]
                            and m.numer == wiersz["numer"]
                        ),
                        None
                    )

                    if miejsce is None:
                        raise ValueError(
                            "Miejsce nie należy do sali seansu."
                        )

                    wybrane_miejsca.append(miejsce)

                rezerwacja = Rezerwacja(
                    row["rezerwacja_id"],
                    seans,
                    wybrane_miejsca
                )

                rezerwacja.status = row["status"]
                rezerwacja.statusPlatnosci = row["status_platnosci"]
                rezerwacja.cenaCalkowita = row["cena_calkowita"]

                rezerwacje.append(rezerwacja)
                seans.rezerwacje.append(rezerwacja)

        return list(seanse.values()), rezerwacje
