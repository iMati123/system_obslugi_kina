
import tkinter as tk
from tkinter import messagebox, ttk

from .system_kina import SystemKina


class AplikacjaKina(ttk.Frame):
    def __init__(self, okno: tk.Tk, system: SystemKina):
        super().__init__(okno, padding=20)

        self.system = system
        self.okno = okno
        self.seans_id = tk.StringVar()

        okno.title("System obsługi kina")
        okno.geometry("800x520")
        okno.minsize(650, 420)

        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(
            self,
            text="SYSTEM OBSŁUGI KINA",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Repertuar
        ramka_repertuar = ttk.LabelFrame(
            self, text="Repertuar", padding=10
        )
        ramka_repertuar.grid(
            row=1, column=0, sticky="nsew"
        )
        ramka_repertuar.columnconfigure(0, weight=1)
        ramka_repertuar.rowconfigure(0, weight=1)

        kolumny = ("id", "film", "termin", "sala", "cena")

        self.tabela = ttk.Treeview(
            ramka_repertuar,
            columns=kolumny,
            show="headings",
            height=6
        )

        naglowki = {
            "id": ("ID", 55),
            "film": ("Film", 190),
            "termin": ("Data i godzina", 160),
            "sala": ("Sala", 145),
            "cena": ("Cena biletu", 100),
        }

        for kolumna, (tekst, szerokosc) in naglowki.items():
            self.tabela.heading(kolumna, text=tekst)
            self.tabela.column(kolumna, width=szerokosc)

        self.tabela.grid(
            row=0, column=0, sticky="nsew"
        )

        pasek = ttk.Scrollbar(
            ramka_repertuar,
            orient="vertical",
            command=self.tabela.yview
        )
        pasek.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=pasek.set)

        self.tabela.bind(
            "<<TreeviewSelect>>", self.wybierzSeans
        )

        ttk.Button(
            ramka_repertuar,
            text="Odśwież repertuar",
            command=self.odswiezRepertuar
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

        # Dostępność miejsc
        ramka_miejsca = ttk.LabelFrame(
            self, text="Dostępność miejsc", padding=10
        )
        ramka_miejsca.grid(
            row=2, column=0, sticky="ew", pady=(12, 0)
        )
        ramka_miejsca.columnconfigure(1, weight=1)

        ttk.Label(
            ramka_miejsca, text="ID seansu:"
        ).grid(row=0, column=0, padx=(0, 10))

        ttk.Entry(
            ramka_miejsca,
            textvariable=self.seans_id,
            width=12
        ).grid(row=0, column=1, sticky="w")

        ttk.Button(
            ramka_miejsca,
            text="Sprawdź wolne miejsca",
            command=self.pokazWolneMiejsca
        ).grid(row=0, column=2, padx=(10, 0))

        self.lista_miejsc = tk.Listbox(
            ramka_miejsca, height=5
        )
        self.lista_miejsc.grid(
            row=1, column=0, columnspan=3,
            sticky="ew", pady=(10, 0)
        )

        self.komunikat = ttk.Label(
            ramka_miejsca,
            text="Wybierz seans z tabeli."
        )
        self.komunikat.grid(
            row=2, column=0, columnspan=3,
            sticky="w", pady=(8, 0)
        )

        self.odswiezRepertuar()

    def odswiezRepertuar(self):
        self.tabela.delete(*self.tabela.get_children())

        for seans in self.system.przegladajSeanse():
            self.tabela.insert("", tk.END, values=(
                seans.id,
                seans.film.tytul,
                seans.dataGodzina.strftime("%d.%m.%Y %H:%M"),
                seans.sala.nazwa,
                f"{seans.cenaBiletu:.2f} zł"
            ))

        self.lista_miejsc.delete(0, tk.END)
        self.komunikat.config(
            text="Wybierz seans z tabeli."
        )

    def wybierzSeans(self, _zdarzenie):
        zaznaczenie = self.tabela.selection()

        if zaznaczenie:
            dane = self.tabela.item(
                zaznaczenie[0], "values"
            )
            self.seans_id.set(dane[0])

            self.lista_miejsc.delete(0, tk.END)
            self.komunikat.config(
                text="Kliknij 'Sprawdź wolne miejsca'."
            )

    def pokazWolneMiejsca(self):
        try:
            seans_id = int(self.seans_id.get())

            wolne_miejsca = (
                self.system.sprawdzDostepnosc(seans_id)
            )

        except ValueError as blad:
            messagebox.showerror(
                "Błąd", str(blad), parent=self.okno
            )
            return

        self.lista_miejsc.delete(0, tk.END)

        for miejsce in wolne_miejsca:
            self.lista_miejsc.insert(
                tk.END, miejsce.pobierzOznaczenie()
            )

        self.komunikat.config(
            text=f"Seans {seans_id}: "
                 f"wolnych miejsc: {len(wolne_miejsca)}"
        )
