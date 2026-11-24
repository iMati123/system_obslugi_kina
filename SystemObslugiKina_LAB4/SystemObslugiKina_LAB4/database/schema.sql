
CREATE TABLE IF NOT EXISTS filmy (
    film_id INTEGER PRIMARY KEY,
    tytul TEXT NOT NULL,
    czas_trwania INTEGER NOT NULL CHECK (czas_trwania > 0),
    gatunek TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sale (
    sala_id INTEGER PRIMARY KEY,
    nazwa TEXT NOT NULL,
    liczba_rzedow INTEGER NOT NULL CHECK (liczba_rzedow > 0),
    miejsc_w_rzedzie INTEGER NOT NULL CHECK (miejsc_w_rzedzie > 0)
);

CREATE TABLE IF NOT EXISTS miejsca (
    miejsce_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    rzad INTEGER NOT NULL CHECK (rzad > 0),
    numer INTEGER NOT NULL CHECK (numer > 0),
    UNIQUE(sala_id, rzad, numer),
    FOREIGN KEY (sala_id) REFERENCES sale(sala_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seanse (
    seans_id INTEGER PRIMARY KEY,
    film_id INTEGER NOT NULL,
    sala_id INTEGER NOT NULL,
    data_godzina TEXT NOT NULL,
    cena_biletu REAL NOT NULL CHECK (cena_biletu >= 0),
    FOREIGN KEY (film_id) REFERENCES filmy(film_id),
    FOREIGN KEY (sala_id) REFERENCES sale(sala_id)
);

CREATE TABLE IF NOT EXISTS rezerwacje (
    rezerwacja_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seans_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'aktywna'
        CHECK (status IN ('aktywna', 'anulowana')),
    status_platnosci TEXT NOT NULL DEFAULT 'nieoplacona'
        CHECK (status_platnosci IN ('nieoplacona', 'oplacona')),
    cena_calkowita REAL NOT NULL CHECK (cena_calkowita >= 0),
    FOREIGN KEY (seans_id) REFERENCES seanse(seans_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rezerwacja_miejsca (
    rezerwacja_id INTEGER NOT NULL,
    miejsce_id INTEGER NOT NULL,
    PRIMARY KEY (rezerwacja_id, miejsce_id),
    FOREIGN KEY (rezerwacja_id)
        REFERENCES rezerwacje(rezerwacja_id) ON DELETE CASCADE,
    FOREIGN KEY (miejsce_id) REFERENCES miejsca(miejsce_id)
);

CREATE INDEX IF NOT EXISTS idx_rezerwacje_seans
    ON rezerwacje(seans_id);

CREATE INDEX IF NOT EXISTS idx_rezerwacja_miejsca_miejsce
    ON rezerwacja_miejsca(miejsce_id);
