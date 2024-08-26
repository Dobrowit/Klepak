import requests
import json
import random
import pathlib
import tkinter as tk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "tester.ui"
RESOURCE_PATHS = [PROJECT_PATH]
DATAOK = 3
LOOP = 30

def generate_data():
    # Generowanie losowych danych
    if DATAOK==1:
        category = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 99])
        user = random.choice(["d4fb8586-101f-4dff-a91e-2488b8214ba3", "9389f8dd-18f8-444a-8dd7-4c815f349a6f"])
        message = random.choice(["Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ut consectetur est.", "In dictum egestas erat vel convallis. Curabitur vestibulum dui a dui faucibus, eget egestas est consequat. Praesent auctor purus et pharetra porttitor. Curabitur sed consectetur ante. Donec tincidunt aliquet euismod. Morbi tristique pellentesque ipsum, eu faucibus nunc pharetra vel. Integer cursus iaculis felis eu tempor. Phasellus et fringilla lectus, et convallis tortor. Integer et dictum tortor. Nam malesuada erat lorem, at accumsan quam blandit vitae."])
        latitude = random.uniform(54.74, 54.77)
        longitude = random.uniform(17.53, 17.57)
    if DATAOK==2:
        category = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 99, 444,])
        user = random.choice(["d4fb8586-101f-4dff-a91e-2488b8214ba3", "9389f8dd-18f8-444a-8dd7-4c815f349a6f", "", "uhbubuy7689"])
        message = random.choice(["","Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ut consectetur est. In dictum egestas erat vel convallis. Curabitur vestibulum dui a dui faucibus, eget egestas est consequat. Praesent auctor purus et pharetra porttitor. Curabitur sed consectetur ante. Donec tincidunt aliquet euismod. Morbi tristique pellentesque ipsum, eu faucibus nunc pharetra vel. Integer cursus iaculis felis eu tempor. Phasellus et fringilla lectus, et convallis tortor. Integer et dictum tortor. Nam malesuada erat lorem, at accumsan quam blandit vitae."])
        latitude = random.uniform(54.74, 54.77)
        longitude = random.uniform(17.53, 17.57)
    if DATAOK==3:
        opisy = {
            "1": [
                "Uszkodzona latarnia uliczna przy ul. Lipowej 12, nie świeci.",
                "Brak pokrywy studzienki na rogu ulicy Kowalskiej, potencjalne zagrożenie.",
                "Uszkodzony chodnik na ul. Polnej, kafle są poluzowane.",
                "Zerwana barierka ochronna na moście nad rzeką Białą.",
                "Pęknięta rura wodociągowa na skrzyżowaniu ul. Nowej i Starej.",
                "Wygięta barierka ochronna na przystanku autobusowym przy ul. Leśnej.",
                "Zerwany przewód elektryczny zwisa z latarni przy ul. Krótkiej.",
                "Uszkodzony dach wiaty na przystanku autobusowym przy ul. Łąkowej.",
                "Wyłamane drzwi do altany śmietnikowej na osiedlu Słonecznym.",
                "Zerwana linka mocująca przy huśtawce na placu zabaw w parku miejskim."
            ],
            "2": [
                "Znak stop przy ul. Długiej jest przewrócony.",
                "Nieczytelny znak informacyjny przy ul. Sienkiewicza.",
                "Błędne oznakowanie objazdu na ul. Mazowieckiej, prowadzi w ślepą uliczkę.",
                "Znak zakazu wjazdu na ul. Pięknej został przesunięty.",
                "Zasłonięty znak ograniczenia prędkości na ul. Morskiej przez gałęzie drzewa.",
                "Znak ostrzegawczy o robotach drogowych przy ul. Zielonej jest nieaktualny.",
                "Znak drogowy przy ul. Wspólnej jest uszkodzony, ledwo widoczny.",
                "Nieprawidłowo ustawiony znak kierunku na rondzie przy ul. Głównej.",
                "Zbyt nisko zawieszony znak przejścia dla pieszych na ul. Sosnowej.",
                "Znak informujący o skrzyżowaniu przy ul. Jasnej jest obrócony w złym kierunku."
            ],
            "3": [
                "Głębokie dziury na ul. Szkolnej utrudniają ruch.",
                "Zapadnięty fragment jezdni na ul. Kwiatowej.",
                "Pęknięcia w nawierzchni asfaltowej na ul. Ogrodowej.",
                "Dziura w jezdni na rondzie przy ul. Dąbrowskiego.",
                "Zapadnięta studzienka kanalizacyjna na ul. Parkowej.",
                "Wyboje na ul. Wierzbowej, niebezpieczne dla rowerzystów.",
                "Przetarcia asfaltu na ul. Królewskiej, wymagają naprawy.",
                "Uszkodzona nawierzchnia na skrzyżowaniu ul. Klonowej i Lipowej.",
                "Pofałdowana jezdnia na ul. Piastowskiej, kierowcy muszą omijać.",
                "Koleiny na ul. Łącznej, bardzo niebezpieczne podczas deszczu."
            ],
            "4": [
                "Pomalowane graffiti na murze przy ul. Wrocławskiej.",
                "Zniszczone ławki w parku przy ul. Szkolnej.",
                "Wybite szyby w wiacie przystankowej przy ul. Długiej.",
                "Zniszczona tablica informacyjna przy wejściu do parku.",
                "Porozrzucane śmieci wokół kosza na śmieci przy ul. Krzywej.",
                "Zdewastowane ogrodzenie na placu zabaw przy ul. Zielonej.",
                "Połamane gałęzie drzew w parku miejskim, możliwy akt wandalizmu.",
                "Pomazane farbą okna w szkole przy ul. Nowej.",
                "Zniszczone rośliny w miejskim ogrodzie na ul. Ogrodowej.",
                "Przewrócone kosze na śmieci na skwerze przy ul. Kościelnej."
            ],
            "5": [
                "Otwarta studzienka na ul. Kościuszki, brak zabezpieczeń.",
                "Brak ogrodzenia przy placu budowy na ul. Świętojańskiej.",
                "Niezabezpieczony wykop na ul. Dębowej, grozi upadkiem.",
                "Uszkodzone barierki ochronne na moście przy ul. Jagiellońskiej.",
                "Niezabezpieczony teren wokół usuniętego drzewa na ul. Leśnej.",
                "Nieoznaczone miejsce robót drogowych na ul. Królowej Jadwigi.",
                "Brak barierek na ścieżce rowerowej przy ul. Lipowej, ryzyko wypadku.",
                "Otwarta brama na teren budowy przy ul. Stawowej, dostęp dla niepowołanych osób.",
                "Nieoznaczone miejsce śliskiej nawierzchni na chodniku przy ul. Ogrodowej.",
                "Niezabezpieczony staw w parku miejskim, brak tablic ostrzegawczych."
            ],
            "6": [
                "Brak podjazdu dla wózków inwalidzkich przy wejściu do urzędu na ul. Szerokiej.",
                "Zablokowany dostęp do rampy dla niepełnosprawnych na ul. Dworcowej.",
                "Uszkodzona winda w budynku na ul. Królewskiej, osoby na wózkach mają problem z dostępem.",
                "Zbyt wąski chodnik na ul. Kwiatowej, nie mieści wózka inwalidzkiego.",
                "Brak oznakowania dla osób niewidomych na przejściu dla pieszych przy ul. Morskiej.",
                "Nieprawidłowo zaparkowane samochody blokują rampę dla wózków przy ul. Polnej.",
                "Zbyt wysokie krawężniki na ul. Dąbrowskiego, utrudniają przejazd wózkiem.",
                "Brak sygnałów dźwiękowych na przejściu dla pieszych przy ul. Ogrodowej.",
                "Niedostępna toaleta publiczna dla osób niepełnosprawnych na rynku głównym.",
                "Śliskie schody bez poręczy w budynku urzędu przy ul. Leśnej."
            ],
            "7": [
                "Złamane drzewo nad ścieżką spacerową przy ul. Leśnej.",
                "Luzujące się cegły na kominie budynku przy ul. Zielonej.",
                "Wybuchy petard w parku miejskim po zmroku, ryzyko pożaru.",
                "Wiszące przewody telefoniczne nad ulicą Krótką, mogą spaść.",
                "Zanieczyszczona woda w fontannie na rynku, ryzyko dla zdrowia.",
                "Nieodśnieżony chodnik przy ul. Słonecznej, niebezpieczeństwo poślizgu.",
                "Zwierzęta wałęsające się po osiedlu na ul. Morskiej, mogą być agresywne.",
                "Pęknięta ściana budynku mieszkalnego przy ul. Świerkowej, ryzyko zawalenia.",
                "Zepsuta sygnalizacja świetlna na skrzyżowaniu ul. Dąbrowskiego i Piłsudskiego.",
                "Otwarte drzwi do nieużywanego budynku na ul. Wiosennej, mogą wejść dzieci."
            ],
            "8": [
                "Martwy kot na poboczu ul. Kwiatowej.",
                "Znaleziono martwego ptaka w parku miejskim przy ul. Wierzbowej.",
                "Martwa wiewiórka na chodniku przy ul. Długiej.",
                "Martwy pies przy drodze krajowej na ul. Słonecznej.",
                "Martwy gołąb na rynku głównym, leży obok fontanny.",
                "Martwe zwierzę, prawdopodobnie jeż, przy ul. Ogrodowej.",
                "Znaleziono martwego szczura w piwnicy budynku przy ul. Zielonej.",
                "Martwe ryby w stawie na ul. Stawowej.",
                "Martwy królik na osiedlu przy ul. Wspólnej.",
                "Martwy jeż na ścieżce rowerowej przy ul. Krótkiej."
            ],
            "9": [
                "Porzucone worki ze śmieciami przy lesie na ul. Leśnej.",
                "Porzucone opony na poboczu ul. Zielonej.",
                "Stare meble porzucone na chodniku przy ul. Sienkiewicza.",
                "Odpady budowlane wyrzucone na dzikim wysypisku przy ul. Polnej.",
                "Porzucone śmieci w parku miejskim przy ul. Szkolnej.",
                "Porzucone butelki i puszki na placu zabaw przy ul. Wierzbowej.",
                "Sterta śmieci na poboczu drogi na ul. Lipowej.",
                "Porzucone materiały niebezpieczne, takie jak azbest, przy ul. Morskiej.",
                "Worki z odpadami wyrzucone w lesie przy ul. Dębowej.",
                "Porzucone śmieci na parkingu przy ul. Głównej, obok marketu."
            ],
            "10": [
                "Czarny dym z komina domu przy ul. Polnej, możliwe spalanie odpadów.",
                "Silny zapach spalenizny na osiedlu przy ul. Kwiatowej, ktoś spala śmieci.",
                "Palenie śmieci w ogrodzie domu na ul. Wierzbowej, nieprzyjemny zapach.",
                "Widoczny dym i spalony plastik w kontenerze przy ul. Słonecznej.",
                "Czarny dym unoszący się nad domem przy ul. Krótkiej, możliwe spalanie odpadów.",
                "Intensywny zapach spalenizny na ul. Zielonej, dochodzi z jednego z domów.",
                "Palone śmieci w beczce na podwórku przy ul. Ogrodowej, zadymienie okolicy.",
                "Palenie liści i plastikowych butelek na działce przy ul. Leśnej.",
                "Dym o intensywnym zapachu plastiku na ul. Jasnej, ktoś spala odpady.",
                "Czarny dym i duszący zapach w okolicy ul. Stawowej, podejrzenie spalania śmieci."
            ],
            "11": [
                "Wyrąb drzew w parku miejskim przy ul. Słonecznej, brak zgody na wycinkę.",
                "Zniszczone krzewy i kwiaty na klombie przy ul. Leśnej.",
                "Spalona trawa w parku przy ul. Zielonej, możliwe podpalenie.",
                "Wycięte drzewa na terenie rezerwatu przy ul. Stawowej.",
                "Porozrzucane śmieci w lesie przy ul. Wierzbowej, niszczenie środowiska.",
                "Wypalona ziemia na skraju lasu przy ul. Ogrodowej.",
                "Zniszczony młody las przy ul. Lipowej, wycięte drzewa.",
                "Wyrzucone odpady chemiczne w strumyku przy ul. Dębowej, zanieczyszczenie wody.",
                "Rozdeptane rabaty kwiatowe w parku miejskim przy ul. Królewskiej.",
                "Wyrzucone opony i inne odpady w lesie przy ul. Kwiatowej."
            ],
            "99": [
                "Zagubione klucze na chodniku przy ul. Wierzbowej.",
                "Głośne hałasy w nocy na ul. Polnej, możliwe zakłócanie ciszy nocnej.",
                "Uszkodzona ławka w parku przy ul. Długiej, grozi przewróceniem.",
                "Bezdomny pies błąkający się po ul. Królewskiej.",
                "Zablokowany wjazd do garażu na ul. Ogrodowej przez nieprawidłowo zaparkowany samochód.",
                "Uszkodzony znak drogowy na ul. Słonecznej, wymaga naprawy.",
                "Zagubiony telefon komórkowy znaleziony na przystanku autobusowym przy ul. Leśnej.",
                "Zablokowane drzwi wejściowe do budynku przy ul. Zielonej, nie da się wejść.",
                "Otwarta furtka na plac zabaw przy ul. Pięknej, dzieci mogą się wydostać.",
                "Zgłoszenie podejrzanej osoby kręcącej się po osiedlu przy ul. Stawowej."
            ]
        }

        nazwa_kategorii = {
            "1": "Uszkodzenie infrastruktury",
            "2": "Złe znaki drogowe",
            "3": "Uszkodzona jezdnia",
            "4": "Wandalizm",
            "5": "Niezabezpieczone otoczenie",
            "6": "Niebezpieczeństwo dla osób niepełnosprawnych",
            "7": "Inne niebezpieczeństwa",
            "8": "Martwe zwierzę",
            "9": "Porzucone śmieci",
            "10": "Spalanie śmieci",
            "11": "Dewastacja przyrody",
            "99": "Inne"
        }

        # Wyświetlanie wyniku
        category = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 99])        
        numer_kategorii = random.choice(list(opisy.keys()))
        losowy_opis = random.choice(opisy[numer_kategorii])
        print(f"Kategoria: [{numer_kategorii}] {nazwa_kategorii[numer_kategorii]}\nOpis: {losowy_opis}")
        user = random.choice(["d4fb8586-101f-4dff-a91e-2488b8214ba3", "9389f8dd-18f8-444a-8dd7-4c815f349a6f"])
        message = losowy_opis
        latitude = random.uniform(54.74, 54.77)
        longitude = random.uniform(17.53, 17.57)
    
    # Tworzenie słownika
    data = {
        "Category": category,
        "Latitude": latitude,
        "Longitude": longitude,
        "UserId": user,
        "Message": message,
        "Base64Image": "/9j/4AAQSkZJRgABAQEBLAEsAAD//gATQ3JlYXRlZCB3aXRoIEdJTVD/4gKwSUNDX1BST0ZJTEUAAQEAAAKgbGNtcwRAAABtbnRyUkdCIFhZWiAH6AAIABcAEAAmACRhY3NwTVNGVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWxjbXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1kZXNjAAABIAAAAEBjcHJ0AAABYAAAADZ3dHB0AAABmAAAABRjaGFkAAABrAAAACxyWFlaAAAB2AAAABRiWFlaAAAB7AAAABRnWFlaAAACAAAAABRyVFJDAAACFAAAACBnVFJDAAACFAAAACBiVFJDAAACFAAAACBjaHJtAAACNAAAACRkbW5kAAACWAAAACRkbWRkAAACfAAAACRtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACQAAAAcAEcASQBNAFAAIABiAHUAaQBsAHQALQBpAG4AIABzAFIARwBCbWx1YwAAAAAAAAABAAAADGVuVVMAAAAaAAAAHABQAHUAYgBsAGkAYwAgAEQAbwBtAGEAaQBuAABYWVogAAAAAAAA9tYAAQAAAADTLXNmMzIAAAAAAAEMQgAABd7///MlAAAHkwAA/ZD///uh///9ogAAA9wAAMBuWFlaIAAAAAAAAG+gAAA49QAAA5BYWVogAAAAAAAAJJ8AAA+EAAC2xFhZWiAAAAAAAABilwAAt4cAABjZcGFyYQAAAAAAAwAAAAJmZgAA8qcAAA1ZAAAT0AAACltjaHJtAAAAAAADAAAAAKPXAABUfAAATM0AAJmaAAAmZwAAD1xtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAEcASQBNAFBtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEL/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2P/2wBDARESEhgVGC8aGi9jQjhCY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2P/wgARCABkAGQDAREAAhEBAxEB/8QAFwABAQEBAAAAAAAAAAAAAAAAAAECA//EABgBAQEBAQEAAAAAAAAAAAAAAAABAgME/9oADAMBAAIQAxAAAAGertVAC2hQAC5nOlFIAUgBaXExotuJN0kgMmgVpd888rWltpEmE0ZNBaq9eeeFt01qoykxJaBRW7enPPDV1q6qRmSZk1UAXTa9MTiXdtSTMTJoEMS9b0XacsG6SRkCkMRF666G65QxJUqADMZN3WrutnKEmcxAEFtqGtXpWjlJICrEIURDWrurJziVpaSTNUQiVrV0WTmtrRYwkWhJC3VaH//EABwQAAEEAwEAAAAAAAAAAAAAABEAASAwEEBBUP/aAAgBAQABBQLd7A2itrWo7BtB00jE0DBRwPM//8QAGhEAAwEBAQEAAAAAAAAAAAAAAAEwESBAEP/aAAgBAwEBPwHy6aab6lVVVVRCohUQqqi7fS+//8QAFBEBAAAAAAAAAAAAAAAAAAAAcP/aAAgBAgEBPwEp/8QAFBABAAAAAAAAAAAAAAAAAAAAcP/aAAgBAQAGPwIp/8QAHRAAAgIDAQEBAAAAAAAAAAAAAREAIBAhMDFAUf/aAAgBAQABPyHmouwOXyBgUBLwlRgU9cBQ+T1dQGoN0J3lQhGAsXKBuhDmxU4fxE4NVO4Y2I0aImgfSOoz/9oADAMBAAIAAwAAABDrfwg20bMJItuUOWP8/oK+RBwh5XGt8S78AxJSx+WlOcjPq3fZ3U80BsVgFWdPJw0Ivd7/ANka6t6fuLVOqFaAf//EABsRAAMBAQEBAQAAAAAAAAAAAAABESAQITAx/9oACAEDAQE/EKUpSlKVHh525pSlwEKXVKUpRCXhSi4+UuS/BCEhjHuhCEMb0uUJC42PS5QuUbwsi63lfAZCD4tj4kQZCDRBYQSIPD4guoWE48v/xAAcEQACAgMBAQAAAAAAAAAAAAABEQAgEDBAMVD/2gAIAQIBAT8Q+E9bwtYqLmCo0ChodBgoZ5HUmKCyw44osjpHB//EAB8QAQACAgIDAQEAAAAAAAAAAAEAERAgITFBUXGBkf/aAAgBAQABPxDFSiUSiUSiUSiUSmBCVvcuXLwDCW8nvW/o2DFKLui8qIvGPpkyIMOO75HQwEEMM7Pk7vkckMEJwXi4EYx5EiHI8SoxidVhgi5/s5COrKCh5l1vBDNSvMtfUA98aIO2XcQNX49wgohlgOxF8Mr2k+EfhBHI/sod8xhoXAaVHBDQJUdHA0Mujq//2Q=="
    }
    
    return data

class AppUI:
    def __init__(self, master=None, on_first_object_cb=None):
        self.builder = pygubu.Builder(on_first_object=on_first_object_cb)
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object("toplevel1", master)
        self.builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def btn_genpost(self):
        for i in range(1, LOOP + 1):
            self.btn_gen()
            self.btn_post()
            print(f"{i}/{LOOP}")

    def btn_gen(self):
        data = generate_data()
        data = json.dumps(data, indent=0)

        url_entry_o = self.builder.get_object('url_entry')
        url_entry_o.delete(0, tk.END)
        url_entry_o.insert(0, "https://klepak.cytr.us/upload")

        json_text_o = self.builder.get_object('json_text')
        json_text_o.delete(1.0, tk.END)
        json_text_o.insert(tk.END, data)

    def btn_get(self):
        url = self.builder.get_object('url_entry').get()
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            self.display_response(response)
        except requests.RequestException as e:
            self.display_error(str(e))

    def btn_post(self):
        url = self.builder.get_object('url_entry').get()
        try:
            data = json.loads(self.builder.get_object('json_text').get("1.0", tk.END))
            response = requests.post(url, json=data)
            self.display_response(response)
        except json.JSONDecodeError:
            self.display_error("Invalid JSON data")
        except requests.RequestException as e:
            self.display_error(str(e))

    def display_response(self, response):
        response_text = self.builder.get_object('response_text')
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, f"Status Code: {response.status_code}\n\n")
        try:
            response_text.insert(tk.END, json.dumps(response.json(), indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            response_text.insert(tk.END, response.text)

    def display_error(self, error_message):
        response_text = self.builder.get_object('response_text')
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, f"Error: {error_message}")

if __name__ == "__main__":
    app = AppUI()
    app.run()
