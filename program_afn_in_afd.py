import graphviz
import tkinter as tk
from PIL import Image, ImageTk
import os


class AFN:
    def __init__(self, stari, alfabet, tranzitii, stare_initiala, stari_finale):
        self.stari = stari
        self.alfabet = alfabet
        self.tranzitii = tranzitii
        self.stare_initiala = stare_initiala
        self.stari_finale = stari_finale

    def inchidere_epsilon(self, stari):
        inchidere = set(stari)
        stiva = list(stari)
        while stiva:
            stare = stiva.pop()
            if ('', stare) in self.tranzitii:
                for urmatoarea_stare in self.tranzitii[('', stare)]:
                    if urmatoarea_stare not in inchidere:
                        inchidere.add(urmatoarea_stare)
                        stiva.append(urmatoarea_stare)
        return frozenset(inchidere)

    def mutare(self, stari, simbol):
        stari_mutare = set()
        for stare in stari:
            if (simbol, stare) in self.tranzitii:
                stari_mutare.update(self.tranzitii[(simbol, stare)])
        return self.inchidere_epsilon(stari_mutare)

    def afn_in_afd(self):
        afd_stari = set()
        afd_tranzitii = {}
        afd_stare_initiala = self.inchidere_epsilon({self.stare_initiala})
        afd_stari_finale = set()

        stiva = [afd_stare_initiala]
        while stiva:
            stari_curente = stiva.pop()
            afd_stari.add(stari_curente)

            for simbol in self.alfabet:
                stari_urmatoare = self.mutare(stari_curente, simbol)
                if stari_urmatoare:
                    afd_tranzitii[(stari_curente, simbol)] = stari_urmatoare
                    if stari_urmatoare not in afd_stari:
                        stiva.append(stari_urmatoare)

            if any(stare in self.stari_finale for stare in stari_curente):
                afd_stari_finale.add(stari_curente)

        return AFD(afd_stari, self.alfabet, afd_tranzitii,
                   afd_stare_initiala, afd_stari_finale)

    def deseneaza_afn(self):
        graf = graphviz.Digraph(format='png')
        graf.attr(rankdir='LR')
        graf.attr(size='5,5')

        for stare in self.stari:
            if stare in self.stari_finale:
                graf.node(stare, shape='doublecircle')
            else:
                graf.node(stare)

        graf.node('', shape='none')
        graf.edge('', self.stare_initiala, label='')

        for (simbol, stare_initiala), stari_urmatoare in self.tranzitii.items():
            for stare_urmatoare in stari_urmatoare:
                graf.edge(stare_initiala, stare_urmatoare, label=simbol)

        graf.render(filename='afn_diagrama', directory='', cleanup=True)


class AFD:
    def __init__(self, stari, alfabet, tranzitii, stare_initiala, stari_finale):
        self.stari = stari
        self.alfabet = alfabet
        self.tranzitii = tranzitii
        self.stare_initiala = stare_initiala
        self.stari_finale = stari_finale

    def stare_to_string(self, stare):
        return ''.join(sorted(list(stare)))

    def __str__(self):
        lines = []
        lg_max_stare = max(len(self.stare_to_string(stare))
                           for stare in self.stari)
        lungime_maxima_tranzitie = max(len(str(tranzitie))
                                       for tranzitie in self.tranzitii)

        lines.append("stări AFD:")
        for stare in self.stari:
            lines.append(self.stare_to_string(stare).ljust(lg_max_stare))
        lines.append("\nTranziții AFD:")
        for tranzitie, stare_urmatoare in self.tranzitii.items():
            tranzitie_str = f"{self.stare_to_string(tranzitie[0])} -> {self.stare_to_string(stare_urmatoare)}".ljust(lungime_maxima_tranzitie)
            lines.append(tranzitie_str)
        lines.append("\nstare inițială AFD:")
        lines.append(self.stare_to_string(self.stare_initiala).ljust(lg_max_stare))
        lines.append("\nstări finale AFD:")
        for stare in self.stari_finale:
            lines.append(self.stare_to_string(stare).ljust(lg_max_stare))
        return '\n'.join(lines)

    def accepta_cuvant(self, cuvant):
        stare_curenta = self.stare_initiala
        for simbol in cuvant:
            if (stare_curenta, simbol) in self.tranzitii:
                stare_curenta = self.tranzitii[(stare_curenta, simbol)]
            else:
                return False
        if stare_curenta in self.stari_finale:
            return "Accepta"
        else:
            return "Nu accepta"

    def get_prefix(self, stare):
        rezultat = ""
        for c in stare:
            if c.isdigit():
                return rezultat
            else:
                rezultat += c

    def get_nume_stare(self, stare):
        stare = ''.join(sorted(list(stare)))
        prefix = self.get_prefix(stare)
        nume = prefix + ''.join([c for c in stare if c.isdigit()])
        return nume

    def deseneaza_afd(self):
        graf = graphviz.Digraph(format='png')
        graf.attr(rankdir='LR')
        graf.attr(size='5,5') 
        graf.attr(overlap='false')
        graf.attr(nodesep='0.5')

        for stare in self.stari:
            nume_stare = self.get_nume_stare(stare)

            if stare in self.stari_finale:
                graf.node(nume_stare, shape='doublecircle')
            else:
                graf.node(nume_stare)

        graf.node('', shape='none')
        nume_stare_initiala = self.get_nume_stare(self.stare_initiala)
        graf.edge('', nume_stare_initiala)

        for tranzitie, stare_urmatoare in self.tranzitii.items():
            stare_initiala = self.get_nume_stare(tranzitie[0])
            stare_urmatoare_nume = self.get_nume_stare(stare_urmatoare)
            graf.edge(stare_initiala, stare_urmatoare_nume,
                      label=str(tranzitie[1]))

        graf.render(filename='afd_diagrama', directory='', cleanup=True)

'''
# Exemplu de utilizare:
afn = AFN(
    stari={'q0', 'q1', 'q2', 'q3', 'q4', 'q5'},
    alfabet={'a', 'b'},
    tranzitii={('a', 'q0'): {'q0', 'q1'}, ('b', 'q0'): {'q0'}, ('b', 'q1'): {'q2'}, ('a', 'q2'): {'q3'},('a', 'q1'): {'q4'}, ('b', 'q3'): {'q5'},('b', 'q4'): {'q5'}},
    stare_initiala='q0',
    stari_finale={'q3','q4'}
)

afn.deseneaza_afn()

afd = afn.afn_in_afd()
print(afd)
afd.deseneaza_afd()

# Testarea cuvintelor
print("\nAFD Acceptă '110':", afd.accepta_cuvant('110'))
print("AFD Acceptă '101':", afd.accepta_cuvant('101'))
print("AFD Acceptă '100010':", afd.accepta_cuvant('100010'))
print("AFD Acceptă '01010':", afd.accepta_cuvant('01010'))
print("AFD Acceptă '00000101':", afd.accepta_cuvant('00000101'))
'''   


def main():
    def citire_si_desenare():
        stari = entry_stari.get().strip().split(',')
        alfabet = entry_alfabet.get().strip().split(',')
        tranzitii = {}
        for tranzitie in entry_tranzitii.get().strip().split(','):
            stare_initiala, simbol, stare_urmatoare = tranzitie.split()
            if (simbol, stare_initiala) in tranzitii:
                tranzitii[(simbol, stare_initiala)].add(stare_urmatoare)
            else:
                tranzitii[(simbol, stare_initiala)] = {stare_urmatoare}
        stare_initiala = entry_stare_initiala.get().strip()
        stari_finale = set(entry_stari_finale.get().strip().split(','))

        afn = AFN(set(stari), set(alfabet), tranzitii,
                  stare_initiala, stari_finale)
        afn.deseneaza_afn()
        afd = afn.afn_in_afd()
        afd.deseneaza_afd()
        afisare_imagini()

    root = tk.Tk()
    root.title("Transformare AFN in AFD")

    # Setează dimensiunea și poziția ferestrei
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width - window_width) // 2
    y_coordinate = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    lbl_stari = tk.Label(root, text="Stări (separate prin virgulă):")
    lbl_stari.grid(row=0, column=0)
    entry_stari = tk.Entry(root)
    entry_stari.grid(row=0, column=1)

    lbl_alfabet = tk.Label(root, text="Alfabet (separate prin virgulă):")
    lbl_alfabet.grid(row=1, column=0)
    entry_alfabet = tk.Entry(root)
    entry_alfabet.grid(row=1, column=1)

    lbl_tranzitii = tk.Label(root,
                             text="Tranziții (în format 'stare_initiala simbol stare_urmatoare', separate prin virgulă):")
    lbl_tranzitii.grid(row=2, column=0)
    entry_tranzitii = tk.Entry(root, width=50)
    entry_tranzitii.grid(row=2, column=1)

    lbl_stare_initiala = tk.Label(root, text="Stare inițială:")
    lbl_stare_initiala.grid(row=3, column=0)
    entry_stare_initiala = tk.Entry(root)
    entry_stare_initiala.grid(row=3, column=1)

    lbl_stari_finale = tk.Label(root, text="Stări finale (separate prin virgulă):")
    lbl_stari_finale.grid(row=4, column=0)
    entry_stari_finale = tk.Entry(root)
    entry_stari_finale.grid(row=4, column=1)

    def submit():
        citire_si_desenare()

    btn_submit = tk.Button(root, text="Submit", command=submit)
    btn_submit.grid(row=5, columnspan=2)

    # Funcția de actualizare a imaginilor
    def refresh():
        # Stergere fișiere PNG existente
        if os.path.exists('afn_diagrama.png'):
            os.remove('afn_diagrama.png')
        if os.path.exists('afd_diagrama.png'):
            os.remove('afd_diagrama.png')
        citire_si_desenare()

    # Funcție pentru afișarea imaginilor
    def afisare_imagini():
        # Afisare imagine AFN
        lbl_afn = tk.Label(root, text="AFN-ul corespunzator")
        lbl_afn.grid(row=6, columnspan=2)
        img_afn = Image.open('afn_diagrama.png')
        img_afn_tk = ImageTk.PhotoImage(img_afn)
        panel_afn.configure(image=img_afn_tk)
        panel_afn.image = img_afn_tk

        # Afisare imagine AFD
        lbl_afn = tk.Label(root, 
                           text="AFD-ul corespunzator (dupa tranformarea din AFN in AFD)")
        lbl_afn.grid(row=8, columnspan=2)
        img_afd = Image.open('afd_diagrama.png')
        img_afd_tk = ImageTk.PhotoImage(img_afd)
        panel_afd.configure(image=img_afd_tk)
        panel_afd.image = img_afd_tk

    # Creare panouri de imagine
    panel_afn = tk.Label(root)
    panel_afn.grid(row=7, column=0, padx=10, pady=10)
    panel_afd = tk.Label(root)
    panel_afd.grid(row=9, column=0, padx=10, pady=10)

    # Creare buton pentru refresh
    # btn_refresh = tk.Button(root, text="Refresh", command=refresh)
    # btn_refresh.grid(row=10, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    main()
