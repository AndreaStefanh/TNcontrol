import datetime
import pyjson5
import json

from typing import Optional, Dict, Any
from enum import IntFlag

class logger:

    @classmethod
    async def error(cls, msg: str, shouldExit: bool = False, timestamp: Optional[str] = None) -> None:
        
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("errorLogs.txt", "a", encoding="utf-8") as logFile:
            logFile.write(f"[{timestamp}] ERROR: {msg}\n")

        if shouldExit:
            exit(-1)
        
        return
    
    @classmethod
    async def apiRequest(cls, url: str, payload: Dict[Any, Any], response_text: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if settings.logApiRequests:
            with open("apiLogs.txt", "a", encoding="utf-8") as logFile:
                logFile.write(f"[{timestamp}] REQUEST TO: {url}\nPAYLOAD: {json.dumps(payload, indent=2, ensure_ascii=False)}\nRESPONSE: {response_text}\n\n")
        
        return

class engineFlags(IntFlag):
    NONE   = 0
    VESUS  = 1
    CIGU18 = 2

class interfaces(IntFlag):
    BASIC_UI = 0
    TELEGRAM = 1

class settings:
    advancedMode = False
    queryName = ""
    selectedEngine: engineFlags = engineFlags.VESUS | engineFlags.CIGU18
    vesusRegionsToQuery = []

    logApiRequests = False
    settingsFile = "settings.json"
    interface: interfaces = interfaces.BASIC_UI
    telegramAPIKey = ""
    telegramAutoRun = False
    telegramAutoRunTime = datetime.time(19, 00)

REGIONS = {
    "Abruzzo":                  "ABR", 
    "Basilicata":               "BAS", 
    "Calabria":                 "CAL", 
    "Campania":                 "CAM", 
    "Emilia-Romagna":           "EMI", 
    "Friuli Venezia Giulia":    "FRI", 
    "Lazio":                    "LAZ", 
    "Liguria":                  "LIG", 
    "Lombardia":                "LOM", 
    "Marche":                   "MAR", 
    "Molise":                   "MOL", 
    "Piemonte":                 "PIE", 
    "Puglia":                   "PUG", 
    "Sardegna":                 "SAR", 
    "Sicilia":                  "SIC", 
    "Toscana":                  "TOS", 
    "Trentino-Alto Adige":      "TRE", 
    "Umbria":                   "UMB", 
    "Valle d’Aosta":            "VAL", 
    "Veneto":                   "VEN",
}

PROVINCE = {
    "AG": "Agrigento",
    "AL": "Alessandria",
    "AN": "Ancona",
    "AO": "Aosta",
    "AR": "Arezzo",
    "AP": "Ascoli Piceno",
    "AT": "Asti",
    "AV": "Avellino",
    "BA": "Bari",
    "BT": "Barletta-Andria-Trani",
    "BL": "Belluno",
    "BN": "Benevento",
    "BG": "Bergamo",
    "BI": "Biella",
    "BO": "Bologna",
    "BZ": "Bolzano",
    "BS": "Brescia",
    "BR": "Brindisi",
    "CA": "Cagliari",
    "CL": "Caltanissetta",
    "CB": "Campobasso",
    "CI": "Carbonia-Iglesias",
    "CE": "Caserta",
    "CT": "Catania",
    "CZ": "Catanzaro",
    "CH": "Chieti",
    "CO": "Como",
    "CS": "Cosenza",
    "CR": "Cremona",
    "KR": "Crotone",
    "CN": "Cuneo",
    "EN": "Enna",
    "FM": "Fermo",
    "FE": "Ferrara",
    "FI": "Firenze",
    "FG": "Foggia",
    "FC": "Forlì-Cesena",
    "FR": "Frosinone",
    "GE": "Genova",
    "GO": "Gorizia",
    "GR": "Grosseto",
    "IM": "Imperia",
    "IS": "Isernia",
    "AQ": "L'Aquila",
    "SP": "La Spezia",
    "LT": "Latina",
    "LE": "Lecce",
    "LC": "Lecco",
    "LI": "Livorno",
    "LO": "Lodi",
    "LU": "Lucca",
    "MC": "Macerata",
    "MN": "Mantova",
    "MS": "Massa-Carrara",
    "MT": "Matera",
    "ME": "Messina",
    "MI": "Milano",
    "MO": "Modena",
    "MB": "Monza e della Brianza",
    "NA": "Napoli",
    "NO": "Novara",
    "NU": "Nuoro",
    "OR": "Oristano",
    "PD": "Padova",
    "PA": "Palermo",
    "PR": "Parma",
    "PV": "Pavia",
    "PG": "Perugia",
    "PU": "Pesaro e Urbino",
    "PE": "Pescara",
    "PC": "Piacenza",
    "PI": "Pisa",
    "PT": "Pistoia",
    "PN": "Pordenone",
    "PZ": "Potenza",
    "PO": "Prato",
    "RG": "Ragusa",
    "RA": "Ravenna",
    "RC": "Reggio Calabria",
    "RE": "Reggio Emilia",
    "RI": "Rieti",
    "RN": "Rimini",
    "RM": "Roma",
    "RO": "Rovigo",
    "SA": "Salerno",
    "SS": "Sassari",
    "SV": "Savona",
    "SI": "Siena",
    "SR": "Siracusa",
    "SO": "Sondrio",
    "TA": "Taranto",
    "TE": "Teramo",
    "TR": "Terni",
    "TO": "Torino",
    "TP": "Trapani",
    "TN": "Trento",
    "TV": "Treviso",
    "TS": "Trieste",
    "UD": "Udine",
    "VA": "Varese",
    "VE": "Venezia",
    "VB": "Verbano-Cusio-Ossola",
    "VC": "Vercelli",
    "VR": "Verona",
    "VV": "Vibo Valentia",
    "VI": "Vicenza",
    "VT": "Viterbo"
}


def loadSettings() -> None:
    global settings

    firstSelectedEngine = True

    try:
        with open(settings.settingsFile, "r", encoding="utf-8") as file:
            settingsData = pyjson5.load(file)

            for key, value in settingsData.items():

                if key == "interface":
                    value = value.lower()
                    if value == "basicui":
                        settings.interface = interfaces.BASIC_UI
                    elif value == "telegram":
                        settings.interface = interfaces.TELEGRAM
                    else:
                        print(f"Error: '{value}' is not a valid interface")
                        exit(-1)
                elif key == "telegramKey":
                    settings.telegramAPIKey = value
                elif key == "queryName":
                    settings.queryName = value
                elif key == "selectedEngine":
                    if firstSelectedEngine:
                        firstSelectedEngine = False
                        settings.selectedEngine = engineFlags.NONE

                    for engine in value:
                        engine = engine.lower()

                        if engine == "vesus" or engine == "ves":
                            settings.selectedEngine |= engineFlags.VESUS
                        elif engine == "cigu18" or engine == "cig":
                            settings.selectedEngine |= engineFlags.CIGU18
                        else:
                            print(f"Error: '{engine}' is not a valid engine")
                            exit(-1)
                elif key == "vesusSelectedRegions":
                    for region in value:
                        region = region.upper()

                        if region in REGIONS.values():
                            settings.vesusRegionsToQuery.append(list(REGIONS.keys()) [list(REGIONS.values()).index(region.upper())])
                        else:
                            print(f"Error: '{region}' is not a valid region")
                            exit(-1)
                elif key == "logApiRequests":
                    if type(value) is not bool:
                        print(f"Error: '{key}' must be a boolean")
                        exit(-1)

                    settings.logApiRequests = bool(value)
                elif key == "telegramAutoRun":
                    if type(value) is not bool:
                        print(f"Error: '{key}' must be a boolean")
                        exit(-1)
                    
                    settings.telegramAutoRun = bool(value)
                elif key == "autoRunTime":
                    try:
                        settings.telegramAutoRunTime = datetime.datetime.strptime(value, "%H:%M")
                    except ValueError:
                        print(f"Error: '{key}' isn't formatted in the HH:MM format")
                        exit(-1)
                else:
                    print(f"Error: '{key}' is not a valid setting")
                    exit(-1)
        
    except FileNotFoundError:
        if not settings.settingsFile == "settings.json":
            print(f"Error: '{settings.settingsFile}' file not found")
            exit(-1)
    except pyjson5.Json5DecodeError:
        print(f"Error: '{settings.settingsFile}' file is not a valid JSON file")
        exit(-1)

    return