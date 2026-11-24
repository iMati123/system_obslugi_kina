from .miejsce import Miejsce


class Sala:

    def __init__(self, numer: int, nazwa: str, liczbaRzedow: int, miejscWRzedzie: int):
        if liczbaRzedow < 1 or miejscWRzedzie < 1:
            raise ValueError("Sala musi mieć przynajmniej jedno miejsce.")

        self.numer = numer
        self.nazwa = nazwa
        self.miejsca = []

        for rzad in range(1, liczbaRzedow + 1):
            for nr_miejsca in range(1, miejscWRzedzie + 1):
                self.miejsca.append(Miejsce(nr_miejsca, rzad))

    def pobierzMiejsca(self) -> list[Miejsce]:
        return self.miejsca.copy()
