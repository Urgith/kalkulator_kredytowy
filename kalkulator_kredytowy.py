import matplotlib.pyplot as plt
from functools import partial
from tkinter import *
import numpy as np


def entry_get(entry):
    return entry.get()


class Interfejs():

    def __init__(self):
        self.root = Tk()
        self.polozenie('Kalkulator kredytowy', '660x650+0+0', 'green')

        self.napis(10, 5, 185, 30, 'Kwota kredytu:')
        self.napis(10, 40, 185, 30, 'Oprocentowanie:')
        self.napis(10, 75, 185, 30, 'Okres kredytowania [lata]:')

        self.napis(395, 40, 185, 30, 'Rodzaj rat:')
        self.napis(395, 5, 185, 30, 'Dodatkowe koszta:')

        self.wzor = self.wejscie(200, 5, 70, 30, 300000)
        self.oprocentowanie = self.wejscie(200, 40, 70, 30, 0.025)
        self.dokladnosc = self.wejscie(200, 75, 70, 30, 30)
        self.raty = self.wejscie(585, 40, 70, 30, 'stałe')
        self.koszta = self.wejscie(585, 5, 70, 30, 0)

        self.przycisk(283, 10, 100, 40, 'Oblicz', partial(self.rysowanie))
        self.przycisk(273, 605, 120, 40, 'Następny wykres', partial(self.next))

        self.canvas = self.create_canvas()
        self.root.mainloop()

    def polozenie(self, nazwa, wymiary, kolor):
        self.root.configure(background=kolor)
        self.root.geometry(wymiary)
        self.root.title(nazwa)

    def przycisk(self, x, y, w, h, napis, f, color='lightCyan3'):
        return Button(self.root, text=napis, command=f, bg=color).place(x=x, y=y, width=w, height=h)

    def wejscie(self, x, y, w, h, val):
        wejscie = Entry(self.root)
        wejscie.insert(END, val)
        wejscie.place(x=x, y=y, width=w, height=h)
        return wejscie

    def napis(self, x, y, w, h, napis):
        return Label(self.root, text=napis).place(x=x, y=y, width=w, height=h)

    def create_canvas(self):
        canvas = Canvas(self.root, width=639, height=480, bg='black')
        canvas.pack()
        canvas.place(x=10, y=120)
        return canvas

    def next(self):
        try:
            self.liczba += 1
            self.canvas.create_image(0, 0, image=self.photos[self.liczba % 2], anchor=NW)

        except:
            pass

    def rysowanie(self):
        self.liczba = 0
        self.photos = []

        Wykres(self)


class Wykres():

    def __init__(self, interfejs):
        self.fig, self.ax = plt.subplots()
        self.wykres = self.fig

        okres = 12 * int(entry_get(interfejs.dokladnosc))
        kredyt = int(entry_get(interfejs.wzor))
        oprocentowanie = float(entry_get(interfejs.oprocentowanie))
        dodatek = float(entry_get(interfejs.koszta))
        raty = entry_get(interfejs.raty)

        czas = np.linspace(0, okres / 12, okres)

        zadluzenie = int(entry_get(interfejs.wzor))
        suma = 0

        if raty == 'malejące':
            czesc_kapitalowa1 = (kredyt / okres)

            kapitalowa = [czesc_kapitalowa1 for i in range(okres)]
            odsetkowa = []
            rata = []
            zadluzenia = [kredyt]

            for i in range(okres):
                czesc_odsetkowa1 = zadluzenie * oprocentowanie / 12
                odsetkowa.append(czesc_odsetkowa1)
                rata.append(czesc_kapitalowa1 + czesc_odsetkowa1)

                zadluzenie -= czesc_kapitalowa1
                zadluzenia.append(zadluzenie)

                suma += czesc_odsetkowa1

        if raty == 'stałe':
            kapitalowa = []
            odsetkowa = []
            zadluzenia = [kredyt]

            sumka = 0
            for i in range(1, okres + 1):
                sumka += (1 + (oprocentowanie / 12))**(-i)

            rat = (kredyt / sumka)
            rata = [rat for i in range(okres)]

            for i in range(okres):
                czesc_odsetkowa1 = zadluzenie * oprocentowanie / 12
                odsetkowa.append(czesc_odsetkowa1)
                kapitalowa.append(rat - czesc_odsetkowa1)

                zadluzenie -= rat - czesc_odsetkowa1
                zadluzenia.append(zadluzenie)

                suma += czesc_odsetkowa1

        if raty == 'stałe':
            plt.plot(list(czas) + [(okres + 1) / 12], zadluzenia, label='Raty:{}'.format(round(rat, 2)))
        else:
            plt.plot(list(czas) + [(okres + 1) / 12], zadluzenia, label='Pierwsza rata:{}, Ostatnia rata:{}'.format(round(rata[0], 2), round(rata[-1], 2)))

        plt.title('Odsetki:{}zł  ;  Do spłaty:{}zł'.format(round(suma, 2), round(kredyt + suma + dodatek, 2)))
        plt.ylabel('Zadłużenie [zł]', fontsize=15)
        plt.xlabel('Lata', fontsize=15)
        plt.ylim([0, (kredyt * 1.01)])
        plt.xlim([0, (okres + 1) // 12])
        plt.tight_layout()
        plt.legend()
        plt.grid()

        self.zapis_canvas(interfejs, 'wykres1.png')
        
        plt.clf()

        czesc_kapitalowa = []
        czesc_odsetkowa = []

        suma_k, suma_o = 0, 0
        for i in range(okres):
            suma_k += kapitalowa[i]
            suma_o += odsetkowa[i]

            if (i % 12) == 11:
                czesc_kapitalowa.append(suma_k)
                czesc_odsetkowa.append(suma_o)
                suma_k, suma_o = 0, 0

        czesc_kapitalowa = np.array(czesc_kapitalowa, dtype=float)
        czesc_odsetkowa = np.array(czesc_odsetkowa, dtype=float)

        plt.bar(range(1, (okres // 12) + 1), czesc_kapitalowa, label='Część kapitałowa')
        plt.bar(range(1, (okres // 12) + 1), czesc_odsetkowa, bottom=czesc_kapitalowa, label='Część odsetkowa')
        plt.title('Odsetki:{}zł  ;  Do spłaty:{}zł'.format(round(suma, 2), round(kredyt + suma + dodatek, 2)))
        plt.ylabel('Suma rocznych rat [zł]', fontsize=15)
        plt.xlabel('Rok', fontsize=15)
        plt.xticks(range(1, (okres // 12) + 1, 2))
        plt.legend(loc='lower right')

        self.zapis_canvas(interfejs, 'wykres2.png')

        interfejs.canvas.create_image(0, 0, image=interfejs.photos[interfejs.liczba % 2], anchor=NW)
        interfejs.root.mainloop()

    def zapis_canvas(self, interfejs, nazwa):
        self.wykres.savefig(nazwa)
        interfejs.photos.append(PhotoImage(file=nazwa))


if __name__=='__main__':
    Interfejs()
