class Miejsce:
    """Pojedyncze miejsce w sali kinowej."""

    def __init__(self, numer: int, rzad: int):
        if numer < 1 or rzad < 1:
            raise ValueError("Numer i rząd miejsca muszą być dodatnie.")

        self.numer = numer
        self.rzad = rzad

    def pobierzOznaczenie(self) -> str:
        return f"rząd {self.rzad}, miejsce {self.numer}"
