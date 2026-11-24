class Film:
    """Informacje o filmie wyświetlanym w kinie."""

    def __init__(self, film_id: int, tytul: str, czasTrwania: int, gatunek: str):
        if not tytul.strip():
            raise ValueError("Tytuł filmu nie może być pusty.")
        if czasTrwania <= 0:
            raise ValueError("Czas trwania filmu musi być dodatni.")

        self.film_id = film_id
        self.tytul = tytul
        self.czasTrwania = czasTrwania
        self.gatunek = gatunek

    def pobierzOpis(self) -> str:
        return f"{self.tytul} — {self.gatunek}, {self.czasTrwania} min"
