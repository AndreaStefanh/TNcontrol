import datetime
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
        
        with open("apiLogs.txt", "a", encoding="utf-8") as logFile:
            logFile.write(f"[{timestamp}] REQUEST TO: {url}\nPAYLOAD: {json.dumps(payload, indent=2, ensure_ascii=False)}\nRESPONSE: {response_text}\n\n")
        
        return

class engineFlags(IntFlag):
    NONE   = 0
    VESUS  = 1
    CIGU18 = 2

class settings:
    queryName = ""
    selectedEngine: engineFlags = engineFlags.VESUS | engineFlags.CIGU18
    vesusRegionsToQuery = []

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