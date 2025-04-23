import asyncio
import aiohttp
import json
import re

from typing import Union, Dict, List, Any
from src.logNSet import settings, logger

ADMIN1ID = {
    "Abruzzo": "SVRBOjMxODM1NjA=",
    "Basilicata": "SVRBOjMxODIzMDY=",
    "Calabria": "SVRBOjI1MjU0Njg=",
    "Campania": "SVRBOjMxODEwNDI=",
    "Emilia-Romagna": "SVRBOjMxNzc0MDE=",
    "Friuli Venezia Giulia": "SVRBOjMxNzY1MjU=",
    "Lazio": "SVRBOjMxNzQ5NzY=",
    "Liguria": "SVRBOjMxNzQ3MjU=",
    "Lombardia": "SVRBOjMxNzQ2MTg=",
    "Marche": "SVRBOjMxNzQwMDQ=",
    "Molise": "SVRBOjMxNzMyMjI=",
    "Piemonte": "SVRBOjMxNzA4MzE=",
    "Puglia": "SVRBOjMxNjk3Nzg=",
    "Sardegna": "SVRBOjI1MjMyMjg=",
    "Sicilia": "SVRBOjI1MjMxMTk=",
    "Toscana": "SVRBOjMxNjUzNjE=",
    "Trentino-Alto Adige": "SVRBOjMxNjUyNDQ=",
    "Umbria": "SVRBOjMxNjUwNDg=",
    "Valle d’Aosta": "SVRBOjMxNjQ4NTc=",
    "Veneto": "SVRBOjMxNjQ2MDQ="
}

async def requestToAPI(logInt: logger, req: Dict[Any, Any]) -> Dict[Any, Any]:
    url = "https://api.vesus.org/graphql"
    header = {"origin": "https://vesus.org"}

    returnResponse = None

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=header, json=req, timeout=aiohttp.ClientTimeout(total=180)) as response:
            if response.status < 200 or response.status > 299:
                text = await response.text()
                await logInt.error(f"UNEXPECTED STATUS CODE: {response.status}\n{text}", shouldExit=True)

            while True:
                line_bytes = await response.content.readline()
                if not line_bytes:
                    break

                line = line_bytes.decode("utf-8").strip()
                if not line:
                    continue

                if line.startswith("{"):
                    returnResponse = line
                    break
                elif line.startswith(":") or line.startswith("event: next"):
                    continue
                elif line.startswith("data: "):
                    returnResponse = line[6:]
                    break
                else:
                    await logInt.error(f"UNEXPECTED RESPONSE LINE: {line}")

    if returnResponse is None:
        await logInt.error("returnResponse is empty", shouldExit=True)

    await logInt.apiRequest(url, req, returnResponse)
    return json.loads(returnResponse)

async def getShortKeys(admin1Id: str, logInt: logger) -> List[str]:
    
    shortKeys = []
    resp = await requestToAPI(logInt, {
        "variables": {
            "after": None,
            "events": {
                "name": "",
                "countryCode": "ITA",
                "admin1Id": admin1Id,
                "admin2Id": None,
                "location": "",
                "start": None,
                "end": None,
                "prizeMoneyMin": None,
                "prizeMoneyMax": None,
                "tournaments": {
                    "type": None,
                    "timeControlType": [],
                    "attendanceMode": None,
                    "rated": None,
                    "roundsMin": None,
                    "roundsMax": None
                }
            },
            "first": 20,
            "scopes": ["FUTURE"]
        },
        "operationName": "EventsListOrganismQuery",
        "docId": "f34274b5926d466168e769c7cb09bacb"
    })

    for event in resp["data"]["events"]["edges"]:
        for tournament in event["node"]["tournaments"]:
            shortKeys.append(tournament["shortKey"])
    
    return shortKeys

async def getTournamentInfo(shortKey: str, names: str, logInt: logger) -> Dict[str, Dict[str, Union[str, List[str]]]]:
    tournamentInfo = await requestToAPI(logInt, {
        "variables": {
            "shortKey": shortKey,
            "hasGames": False, 
            "hasResults": False,
            "hasCompletedPublishedRounds": False,
            "canNoLongerBeUpdated": False,
            "pairingsRound": None,
            "scopes": ["REGISTRATIONSCOUNTS"]
        },
        "operationName": "TournamentPage_Subscription",
        "docId": "5028c4f2454522745e46818479f5c185"
    })

    players = {}

    try:
        namesList = names.split('|')
        namesPartsList = [re.split(r'\s+', name.strip().lower()) for name in namesList]

        registeredPlayers = tournamentInfo["data"]["tournamentUpdate"]["registeredPlayers"]

        filteredPlayers = registeredPlayers
        for nameParts in namesPartsList:
            tempFilteredPlayers = filteredPlayers
            for part in nameParts:
                partLower = part.lower()
                tempFilteredPlayers = [
                    player for player in tempFilteredPlayers
                    if partLower in player["name"].lower()
                ]
            if tempFilteredPlayers:
                for player in tempFilteredPlayers:
                    players.setdefault(shortKey, {
                        "tournament": tournamentInfo["data"]["tournamentUpdate"]["event"]["name"],
                        "location": tournamentInfo["data"]["tournamentUpdate"]["event"]["location"],
                        "endRegistration": tournamentInfo["data"]["tournamentUpdate"]["registrationsEnd"],
                        "startTournament": tournamentInfo["data"]["tournamentUpdate"]["start"],
                        "endTournament": tournamentInfo["data"]["tournamentUpdate"]["end"],
                        "names": []
                    })["names"].append(player["name"])
    finally:
        return players

async def query(logInt: logger) -> List[Dict[str, Dict[str, Union[str, List[str]]]]]:
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for region in settings.vesusRegionsToQuery:
            if region in ADMIN1ID:
                tasks.append(tg.create_task(getShortKeys(ADMIN1ID[region], logInt)))
            else:
                await logInt.error(f"Unknown region: {region}", shouldExit=True)
    result = [task.result() for task in tasks]
    
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for region in result:
            for shortKey in region:
                tasks.append(tg.create_task(getTournamentInfo(shortKey, settings.queryName, logInt)))
    result = [r for r in (task.result() for task in tasks) if r]

    return result