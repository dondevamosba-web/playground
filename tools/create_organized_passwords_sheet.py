#!/usr/bin/env python3
"""
Creates a new organized Google Sheet with password data categorized by tabs.
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1KIdhU3flc5QTb-hv5T-1uPNCFBSMFFIoCuMCQnDqlqs"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_creds():
    creds = Credentials.from_authorized_user_file(
        "/Users/guidocarminatti/Downloads/playground/token_sheets.json", SCOPES
    )
    return creds

# ─── DATA ────────────────────────────────────────────────────────────────────
# Each tab: (tab_name, color_rgb, [(service, user, password, notes), ...])

TABS = [
    ("Bancos & Finanzas", {"red": 0.2, "green": 0.7, "blue": 0.3}, [
        ("AFIP", "20336756007", "Carlitos12", ""),
        ("Rentas", "20336756007", "salimos12", ""),
        ("Nación (web)", "carminattiguido@gmail.com", "guido352 / 1Marica2", "código 2653"),
        ("NACION DEBITO", "", "2444", ""),
        ("Galicia", "guido134 (homebanking)", "Hombkng: 3421", "Cajero 1373 | Token 137313 | 8000 amex 23k visa"),
        ("QUIERO (Galicia pts)", "guido134", "3421", ""),
        ("Galicia Puntos Naranja X", "", "", "sacar?"),
        ("Hipotecario", "Guidokarmi88", "1362", "wpres: guido / Pensala.18@"),
        ("BBVA", "gringo", "Gring452", ""),
        ("Santander (Río)", "homebanking junco143", "4561", "cajero 4353 | Alfanumerica UPE"),
        ("Balanz", "gcarminatti / Ganamos.43", "5426", "186k | código 2653 | nuevo op code julio 2022"),
        ("Brubank", "carminattiguido@gmail.com", "código 482357", "cajero 2464 | 76k"),
        ("Buenbit", "carminattiguido@gmail.com", "Salimos.34!", "pin nuevo 425367 | viejo 245124"),
        ("Belo", "", "", "pin 425367"),
        ("LEMON", "", "523452", "$guidocarmi 35k"),
        ("Deel", "carminattiguido@gmail.com", "Zelanda389!!", ""),
        ("Wise", "carminattiguido@gmail.com", "U2amg394!", ""),
        ("Bitwage", "carminattiguido@gmail.com", "Tatera453!!", ""),
        ("Paypal", "carminattiguido@gmail.com", "uniestados88", "auth G: VC4LA6QSZBBKQCT4"),
        ("Western Union", "carminattiguido@gmail.com", "Salimos.13", ""),
        ("Skrill", "carminattiguido@gmail.com", "Salimos.34!", ""),
        ("Prex", "", "Pensala.18", ""),
        ("global66", "carminattiguido@gmail.com", "Salesforce6!", ""),
        ("Splitwise", "carminattiguido@gmail.com", "Salimos12", ""),
        ("Binance", "carminattiguido@gmail.com", "Ventana18", ""),
        ("Ripio", "carminattiguido@gmail.com", "Salimos.56!", "pin 245164"),
        ("Bitso", "carminattiguido@gmail.com", "ftg345.17A", "nip 482357 | compré 50k en ether"),
        ("bibyt", "dondevamosba@gmail.com", "Petute.54", ""),
        ("dukascopy", "", "Pensala23!!", ""),
        ("IBKR", "guidogrin", "Salimos.18", ""),
        ("Authenticator app", "", "Sálvame.14", ""),
        ("Mercadopago (Tancredi)", "tancredijulian@gmail.com", "salimos12", ""),
        ("Mercadolibre (Tancredi)", "tancredijulian@gmail.com", "Salimos12", ""),
        ("payo", "carminattiguido@gmail.com", "Capacity3000", "cod rec 972V1JIM | seg Margarita | euro pin 0010 | cod compras 186290"),
        ("Amazon (compras)", "carminattiguido@gmail.com", "Salimos.35 / b(vhR2WhmEN)%B)", ""),
        ("Smiles (mamá)", "159866733", "5465", ""),
        ("SMILES", "158500650", "5928", ""),
        ("AerolineasPlus SkyTeam", "58477183", "truco342", "carminattiguido@gmail.com"),
        ("Latam", "54336756009", "uniestados", ""),
        ("AVIANCA Millas Star Alliance", "13498921951", "Salimos.12", "hasta 3 días dps del viaje"),
        ("American Airlines AAdvantage", "7U5HL32", "Salimos.12", "hasta 3 días dps del viaje"),
        ("Iberia Avios", "82301359", "Salimos.12", "hasta 3 días dps del viaje"),
    ]),

    ("Emails & Cuentas", {"red": 0.2, "green": 0.5, "blue": 0.8}, [
        ("Gmail principal", "carminattiguido@gmail.com", "U2amg394", ""),
        ("Gmail", "guidocarminatti@gmail.com", "U2amg394", ""),
        ("Gmail (typo)", "Carminattiguido@gmail.con", "U2amg394", "con typo - recovery"),
        ("Gmail ctrl", "gctrlaltsupr@gmail.com", "uniestados12", ""),
        ("Gmail Tancredi", "tancredijulian@gmail.com", "salimos2", ""),
        ("Gmail Sirzer", "Sirzer.cs@gmail.com", "Salimos12", ""),
        ("Gmail UADE Feba", "febauade@gmail.com", "uade1234", ""),
        ("Gmail Agroservice", "agroserviceba@gmail.com", "elduendemaldito", ""),
        ("Gmail dondevamos", "dondevamosba@gmail.com", "buenosaires", ""),
        ("Gmail ventaentradas", "ventadeentradasba@gmail.com", "Fernan.13!", ""),
        ("Gmail ventaentradas3", "ventadeentradasba3@gmail.com", "buenoaires", ""),
        ("Gmail ventaentradas4", "ventadeentradasba4@gmail.com", "buenosaires", ""),
        ("Gmail ventaentradas5", "ventadeentradasba5@gmail.com", "buenoaires", ""),
        ("Gmail febapilire", "febapilire@gmail.com", "fiestaselectronicasre", ""),
        ("Gmail solucionesgraficas", "solucionesgraficasba@gmail.com", "elduendemaldito", ""),
        ("Gmail mientrada", "mientradaargentina@gmail.com", "guidocapo", ""),
        ("Gmail Galdino", "galdino.srl@gmail.com", "", ""),
        ("Gmail Sociallyin", "guido@sociallyin.com", "U2amg394!", ""),
        ("Hotmail Guido", "guidokarmi@hotmail.com", "Zelanda542", ""),
        ("Hotmail Aristobulo (Tobi)", "aristobulocarminatti@hotmail.com", "Soyelnumero2", ""),
        ("iCloud Rosa", "dondevamosba@gmail.com", "conti45gO (la O es mayúscula)", "cel 1123874173"),
        ("iCloud Guido", "guidokarmi@hotmail.com", "Salimos12", "cel 1162310105"),
        ("iCloud Tobi5s", "tobi.carminatti@icloud.com", "54 9 228 453-2320", ""),
        ("Unidays", "guidoelnuevo@hotmail.com", "", "vence junio 2023"),
        ("Keychain Mac", "", "maruyjustin3", ""),
    ]),

    ("Instagrams", {"red": 0.8, "green": 0.3, "blue": 0.6}, [
        ("guidocarminatti_", "carminattiguido@gmail.com", "Farfala.35", "GUIDOCARMINATTI_"),
        ("guidolate", "dondevamosba@gmail.com", "guidolate", "cel 1123874173"),
        ("fiestaselectronicasbuenosaire", "", "guidocapo", ""),
        ("electronicticketsok", "febapilire@gmail.com", "elduendemaldito", "puede ser agencia"),
        ("elpeloterofc", "", "uniestados", "cosas de fisio"),
        ("pulmotorfc", "", "Zelanda433!", ""),
        ("ClaraMartinez", "Sirzer.cs@gmail.com", "Salimos12", ""),
        ("quemisterioelcontrol", "ventadeentradasba5@gmail.com", "airtag123", ""),
        ("techno.apple.ok", "", "", "febapilere@gmail.com mail de recupero"),
        ("technoyhouseba", "", "", "cel 1123874173 / chip tuenti"),
        ("FEBA (ventaentradas)", "ventadeentradasba@gmail.com", "Pensala2", "pasada a Chasco"),
    ]),

    ("Facebooks", {"red": 0.2, "green": 0.4, "blue": 0.9}, [
        ("Guido Carminatti (principal)", "carminattiguido@gmail.com", "teaviso.12", ""),
        ("Guido Carminatti (viejo)", "febauade@gmail.com", "Saldremos.43", "fb actual: Salimos.12"),
        ("Gui Feba", "", "elduendemaldito", "saleferiaba"),
        ("Alex Villanueva", "dondevamosba@gmail.com", "Persona34!", ""),
        ("Feba Aires", "ventadeentradasba@gmail.com", "Farfala.15", ""),
        ("Feba Pili", "febapilire@gmail.com", "fiestaselectronicasre", ""),
        ("Clara Martinez", "earteba@gmail.com", "elduendemaldito", ""),
        ("Andy Bernal", "solucionesgraficasba@gmail.com", "malditosduendes", ""),
        ("Gui Trejo (30/06/88)", "agroserviceba@gmail.com", "buenosaires", ""),
        ("Ale Santos", "ventadeentradasba4@gmail.com", "Pensala.14!", ""),
        ("Julian Tancredi", "tancredijulian@gmail.com", "Salimos12", ""),
        ("Alejo Mesa", "1132355684", "Salimos12", ""),
        ("Facebook Papa (Tobi)", "tobi.carminatti@gmail.com", "Soyelnumero2", ""),
    ]),

    ("Redes Sociales", {"red": 0.5, "green": 0.8, "blue": 0.9}, [
        ("LinkedIn (Guido)", "carminattiguido@gmail.com", "Salimos12", ""),
        ("LinkedIn (venta)", "ventadeentradasba@gmail.com", "pelotudo", ""),
        ("Twitter", "ventadeentradasba@gmail.com", "palabre43", ""),
        ("Skype", "guidokarmi@hotmail.com", "U2amg394", ""),
        ("Spotify", "11161884413", "patagon1a", ""),
        ("Tumblr", "guidokarmi@hotmail.com", "putoamosoy", ""),
        ("Pinterest", "carminattiguido@gmail.com", "salimos88", ""),
        ("Quora Feba", "ventadeentradasba@gmail.com", "", ""),
        ("Hootsuite", "ventadeentradasba@gmail.com", "U2amg394", ""),
        ("Bitly", "ventadeentradasba@gmail.com", "uniestados", ""),
        ("SocialBlade", "tancredijulian@gmail.com", "utGCTCxxA5te63lXeZvm", ""),
        ("Twitch", "gringb0t", "gatoU.114", ""),
        ("Reddit (ctrl)", "11ctrlalts", "uniestados88", ""),
        ("Owlstat", "carminattiguido@gmail.com", "(entra con Gmail)", ""),
        ("GoodReads", "tancredijulian@gmail.com", "Salimos88", ""),
        ("Mindmeister", "ventadeentradasba@gmail.com", "Salimos12", ""),
        ("Linktree", "dondevamosba@gmail.com", "Salimos.14", ""),
    ]),

    ("Gaming", {"red": 0.6, "green": 0.2, "blue": 0.8}, [
        ("Steam", "carminattiguido@gmail.com", "Conicet18", ""),
        ("Discord Jisso (Windows)", "guidokarmi@hotmail.com", "buenospagos", ""),
        ("Discord Gordzilla (Windows)", "ventadeentradasba@gmail.com", "sudadera23", ""),
        ("Discord highontea (Mac)", "ventadeentradasba5@gmail.com", "", ""),
        ("Discord holatom (Windows)", "dondevamosba@gmail.com", "Salimos12", ""),
        ("Discord lizardface (Mac)", "ventadeentradasba3@gmail.com", "paparulo23", ""),
        ("Discord Tat AleMob", "Guidocarminatti@gmail.con", "Salimos12", ""),
        ("Pokerstars (guidogrin)", "dondevamosba@gmail.com", "lalalayupa123", "yupanquiteam"),
        ("Pokerstars school", "", "12salimos", ""),
        ("Voobly", "sirzer", "s7q38", ""),
        ("3dgames foro", "dondevamosba@gmail.com", "spirulina / patagon1a", ""),
        ("BHW Forum", "l0m1s", "Salimos.14", ""),
        ("Demonoid", "bz2uq1v47z3j", "guidokarmi@hotmail.com", ""),
        ("Dominator", "ventadeentradasba@gmail.com", "stamper12", ""),
        ("Vimeo", "guidokarmi@hotmail.com", "Stamper.12", ""),
    ]),

    ("Trabajo & Tools", {"red": 0.9, "green": 0.6, "blue": 0.2}, [
        ("Asana", "carminattiguido@gmail.com", "Salimos.17", ""),
        ("Basecamp", "guidocarminatti@gmail.com", "Zelanda134", ""),
        ("Basecamp Sociallyin", "guido@sociallyin.com", "Zelanda563!", ""),
        ("Amplitude", "guidocarminatti@gmail.com", "Zelanda134", ""),
        ("Dashlane (viejo)", "", "Zelanda134", ""),
        ("Dashlane Sociallyin", "guido@sociallyin.com", "U2amg394!", ""),
        ("Hubspot (Wideo)", "marketing@wideo.co", "Salimos.14", "Guido Carminatti"),
        ("Sprout Social", "guido@sociallyin.com", "Singapur.15", ""),
        ("Bill.com", "guido@sociallyin.com", "Fernando.13!", ""),
        ("Reportgarden", "guido@sociallyin.com", "Persona.123", ""),
        ("TikTok Manager", "guido@sociallyin.com", "Pensala564!", ""),
        ("TikTok business personal", "carminattiguido@gmail.com", "Salimos.1265", "premierwireless"),
        ("ConvertKit", "carminattiguido@gmail.com", "salimos.15", ""),
        ("ConvertKit (dondevamos)", "dondevamosba@gmail.com", "petute.15", "14 días free a partir 22 julio"),
        ("Phantom Buster", "carminattiguido@gmail.com", "Pensala343", ""),
        ("Wix 360", "", "Performance365.!", ""),
        ("WeWork", "", "Salimos.13", ""),
        ("guido@360a", "", "360Aptreno!", ""),
        ("AppFlyers", "guido@sociallyin.com", "Bailamos.12", ""),
        ("Zoom", "guido@sociallyin.com", "(entra con Gmail Sociallyin)", ""),
        ("Mailchimp", "febaba", "Molesto.14", "dondevamosba@gmail.com"),
        ("IBM", "carminattiguido", "Salimos.12 / Peterete13", ""),
    ]),

    ("Telefonía & Internet", {"red": 0.3, "green": 0.8, "blue": 0.5}, [
        ("Fibertel", "guidokarmi@hotmail.com", "hola1234", ""),
        ("Tuenti (personal)", "carminattiguido@gmail.com", "Fernet.13!", ""),
        ("Tuenti 2", "33675601", "", "cel 1163620664"),
        ("Club Personal", "guidokarmi@hotmail.com (via fibertel)", "hola1234", ""),
        ("MovieClub", "guidokarmi@hotmail.com", "uniestados", ""),
        ("Flow", "guidokarmi@hotmail.com", "hola1234", ""),
        ("AYSA", "carminattiguido@gmail.com", "Nomada.14", ""),
        ("Wifi Casa", "CASA FIBERTEL660", "003367560", ""),
        ("Claro (Tobi)", "tobi.carminatti@gmail.com", "", "2439"),
        ("Claro Empresas", "572548030", "8046", ""),
    ]),

    ("Compras & Misc", {"red": 0.8, "green": 0.5, "blue": 0.2}, [
        ("Dropbox", "guidocarminatti@gmail.com", "(gmail)", ""),
        ("Uber", "carminattiguido@gmail.com", "salimos", "Ale Santos Fb"),
        ("Cabify", "carminattiguido@gmail.com", "Salimos12", ""),
        ("Grabr", "carminattiguido@gmail.com", "salimos12", ""),
        ("CouchSurfing", "carminattiguido@gmail.com", "salimos12", ""),
        ("Bici BA", "carminattiguido@gmail.com", "Salimos.13", ""),
        ("Correo Argentino", "guidocarminatti@gmail.com / carminattiguido@gmail.com", "Carlitos12 / Salimos.15", ""),
        ("El Corte Inglés", "dondevamosba@gmail.com", "po21po", ""),
        ("Infoautos", "guidoctrl", "salimos31", ""),
        ("Coto", "Guido88", "ahoraesmic a", ""),
        ("Día Super", "guidocarminatti@gmail.com", "Entramos15", ""),
        ("mipayo", "", "CtrlAltSupr1", "preferidopalermo12"),
        ("Birthday Alarm", "guidokarmi@hotmail.com", "Salimos.476", ""),
        ("Auto Entrada", "carminattiguido@gmail.com", "Salimos15", ""),
        ("Prenota (Guido)", "carminattiguido@gmail.com", "Salimos12", ""),
        ("Prenota (Papa)", "tobi.carminatti@gmail.com", "Salimos12", ""),
        ("Foro Contadores", "dondevamosba@gmail.com", "salimos12", ""),
        ("UADE", "gcarminatti", "Salimos.19", "UBA XX1: 20336756007 — algo fis quim"),
        ("BOCA soysocio", "carminattiguido@gmail.com", "Fernet.13!", ""),
        ("nubi", "tancredijulian@gmail.com", "Salimos12", ""),
        ("Tambero.com", "dondevamosba@gmail.com", "papafrita", ""),
        ("Agroads", "", "lareputamadre", "alejandro"),
        ("Headspace", "febapilire@gmail.com", "Patagon1a.", ""),
        ("myfitnesspal", "dondevamosba@gmail.com", "salimos12", ""),
        ("Sportclub", "Carminattiguido@gmail.con", "Lapitamadre435", ""),
        ("Italiano (hospital)", "", "Persona.43! / Kristina2020", ""),
        ("Airbnb Tobi", "tobi.carminatti@gmail.com (Facebook Tobi)", "", ""),
        ("Paypal Tobi", "tobi.carminatti@gmail.com", "Ahora30590 / Salimos12", ""),
        ("Paypal Hotmail (Tobi)", "aristobulocarminatti@hotmail.com", "Soyelnumero2", ""),
        ("NACION (Tobi)", "Tobi770", "Paco4543", ""),
        ("LanpassTobi", "54121772828", "aristobulocarminatti@hotmail.com", ""),
        ("Latam Tobi", "", "Soyelnumero2 | 6454 Telefonica", ""),
        ("Terreno Bolívar 25% papa", "011-003000-2", "", ""),
        ("Terreno Parque Arano", "078-054697-2", "", "Partida"),
        ("Mercadolibre (Maru)", "ventadeentradasba3@gmail.com", "uniestados", "hhhmaru@hotmail.com"),
        ("Maru hotmail", "hhhmaru@hotmail.com", "Maruyjustin3 / Maruyjustin88", ""),
    ]),

    ("Venta Entradas", {"red": 0.9, "green": 0.2, "blue": 0.3}, [
        ("TUACCESO", "ventadeentradasba@gmail.com", "internet", ""),
        ("TUACCESO", "dondevamosba@gmail.com", "salimos21", ""),
        ("TUACCESO", "ventadenentradasba@gmail.com", "", ""),
        ("TICKETEK", "carminattiguido@gmail.com", "uniestados", ""),
        ("EMT", "Carlosmontes@gmail.com", "salimos", ""),
        ("Passline", "dondevamosba@gmail.com", "gny2249649 / ceg842", "2022: ceg842"),
        ("Passline", "carminattiguido@gmail.com", "2dx819", ""),
        ("Passline Trucho Nicolás Gómez", "agroserviceba@gmail.com", "Pensala2", ""),
        ("Minha Entrada", "Guido88", "patagon1a", ""),
        ("Nightclubber", "guidokarmi", "internet", ""),
        ("AllAccess", "guidocarminatti@gmail.com", "salimos12", ""),
        ("Casting Club", "Carminattiguido@gmail.com", "Salimos.15", ""),
        ("FAUNA", "carminattiguido@gmail.com", "Palmitos31", ""),
        ("Saigon", "33675600", "Salimos.12", ""),
        ("TheFashionSpot", "MikaLove", "6387436", ""),
        ("Actores online", "", "2444", ""),
    ]),

    ("Clientes Meta", {"red": 0.15, "green": 0.15, "blue": 0.15}, []),  # filled separately
]

META_CLIENTS = [
    ("Luiz", "A&A Painting, Inc.", "$5,000", "Chad"),
    ("Luiz", "Bigger Picture Painting", "$2,500", "Jen"),
    ("Luiz", "Brushes Over Broome LLC", "$2,000", "Chad"),
    ("Luiz", "Carroll Custom Coatings", "$2,400", "Chad"),
    ("Luiz", "Carter's Painting Services", "$2,500", "Josh"),
    ("Luiz", "Five Star Painting Federal Way", "$3,000", "Chad"),
    ("Luiz", "Fridenmaker Painting", "$2,500", "Jen"),
    ("Luiz", "Pilot Painting LLC", "$2,500", "Jen"),
    ("Luiz", "Pivotal Painting LLC", "$2,000", "Jen"),
    ("Luiz", "Roll City Painting", "$2,750", "Jen"),
    ("Luiz", "Roy & Paul Cabinet Painting", "$1,500", "Chad"),
    ("Luiz", "TN Precision Painters", "", "Josh"),
    ("Luiz", "UR Painter", "$2,500", "Josh"),
    ("Luiz", "Visual Paint", "$2,000", "Chad"),
    ("Guido", "Absolute Best Painting", "$2,000", "Chad"),
    ("Guido", "Fresh Coat North Shore", "$2,500", "Jill"),
    ("Guido", "GoEpoxy LLC", "$3,300", "Chad"),
    ("Guido", "Marvelous Painters", "$2,500", "Jen"),
    ("Guido", "Paramount Painting Services", "$2,500", "Bailey"),
    ("Guido", "ProEdge Painting", "$5,000", "Chad"),
    ("Guido", "Starfish Painting", "$3,000", "Chad"),
    ("Guido", "Tera Painting", "$2,500", "Bailey"),
    ("Guido", "We Paint & Renovate", "$1,500", "Chad"),
    ("Guido", "Distintively", "", "Josh"),
    ("Lucas", "Advantage Paint Services", "$3,000", "Bailey"),
    ("Lucas", "Cyr Painting Service", "$2,500", "Josh"),
    ("Lucas", "Ed Wade Painting", "", "Bailey"),
    ("Lucas", "Five Star Painting Wilmington", "$2,500", "Bailey"),
    ("Lucas", "Fresh Coat Vernon Hills", "$2,500", "Josh"),
    ("Lucas", "Greenhaus Painting", "$32,475", "Bailey"),
    ("Lucas", "Interland Design", "$2,500", "Bailey"),
    ("Lucas", "Islanders Choice Painting", "$3,000", "Josh"),
    ("Lucas", "Lines Painting", "$3,300", "Bailey"),
    ("Lucas", "Magna Painting of San Antonio", "$4,500", "Bailey"),
    ("Lucas", "Procoat Painting", "$2,500", "Josh"),
    ("Lucas", "Ukie Painting", "$7,700", "Bailey"),
]


def hex_color(r, g, b):
    return {"red": r, "green": g, "blue": b}


def create_spreadsheet(service):
    body = {
        "properties": {"title": "Passwords & Accounts (Organizado)"},
        "sheets": [{"properties": {"title": t[0]}} for t in TABS],
    }
    ss = service.spreadsheets().create(body=body, fields="spreadsheetId,sheets").execute()
    return ss["spreadsheetId"], {s["properties"]["title"]: s["properties"]["sheetId"] for s in ss["sheets"]}


def build_requests(sheet_id, rows, header, tab_color):
    requests = []

    # Tab color
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "tabColorStyle": {"rgbColor": tab_color}},
            "fields": "tabColorStyle",
        }
    })

    # Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }
    })

    # Data
    values = [header] + list(rows)
    requests.append({
        "updateCells": {
            "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 0},
            "rows": [
                {
                    "values": [
                        {
                            "userEnteredValue": {"stringValue": str(cell)},
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": i == 0,
                                    "foregroundColor": tab_color if i == 0 else {"red": 0.9, "green": 0.9, "blue": 0.9},
                                },
                                "backgroundColor": {"red": 0.15, "green": 0.15, "blue": 0.15} if i == 0
                                    else ({"red": 0.12, "green": 0.12, "blue": 0.12} if row_idx % 2 == 0
                                          else {"red": 0.08, "green": 0.08, "blue": 0.08}),
                                "padding": {"top": 4, "bottom": 4, "left": 8, "right": 8},
                                "verticalAlignment": "MIDDLE",
                            },
                        }
                        for i, cell in enumerate(row)
                    ]
                }
                for row_idx, row in enumerate(values)
            ],
            "fields": "userEnteredValue,userEnteredFormat",
        }
    })

    # Auto-resize columns
    requests.append({
        "autoResizeDimensions": {
            "dimensions": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": len(header)}
        }
    })

    return requests


EXISTING_ID = "1fUmZGaPuc8ro2MqTIu9ZrEeLh-lsgKa_U5b7aBdaTHY"

def main():
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)

    print("Using existing spreadsheet...")
    ss_id = EXISTING_ID
    ss = service.spreadsheets().get(spreadsheetId=ss_id).execute()
    sheet_ids = {s["properties"]["title"]: s["properties"]["sheetId"] for s in ss["sheets"]}
    print(f"https://docs.google.com/spreadsheets/d/{ss_id}")

    all_requests = []

    for tab_name, tab_color, rows in TABS:
        sid = sheet_ids[tab_name]

        if tab_name == "Clientes Meta":
            header = ["Meta Manager", "Cliente", "Budget Meta/mes", "AM"]
            data = META_CLIENTS
        else:
            header = ["Servicio", "Usuario / Email", "Contraseña", "Notas"]
            data = rows

        all_requests.extend(build_requests(sid, data, header, tab_color))

    # Send all in one batch
    service.spreadsheets().batchUpdate(
        spreadsheetId=ss_id,
        body={"requests": all_requests}
    ).execute()

    print(f"Done! https://docs.google.com/spreadsheets/d/{ss_id}")
    return ss_id


if __name__ == "__main__":
    main()
