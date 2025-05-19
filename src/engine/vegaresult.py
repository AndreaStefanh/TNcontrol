import asyncio
import aiohttp
import json
import re

from typing import Union, Optional, List, Dict
from bs4 import BeautifulSoup
from src.logNSet import settings, logger

async def request(logInt: logger, param: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.vegaresult.com/" + param, timeout=aiohttp.ClientTimeout(total=180)) as response:

            if response.status != 200:
                text = await response.text()
                await logInt.error(f"UNEXPECTED STATUS CODE: {response.status} WHILE QUERYNG: https://www.vegaresult.com/vr/{param}\n{text}", shouldExit = True)

            return await response.text()

async def getIds(logInt: logger) -> list[str]:
    tournamentsInfo = await request(logInt, "vr/get_tournaments.php?status=next&timecontrol=all&interest=all&type=all&event=&startdate=&enddate=")
    tournamentsInfo = json.loads(tournamentsInfo)["tournaments"]

    ids = []
    for tornament in tournamentsInfo:
        ids.append(tornament["id"])
    
    return ids

async def getTournamentInfo(logInt: logger, id: str) -> Dict[str, Union[str, List[Dict[str, Optional[str]]]]]:
    tournamentInfo = await request(logInt, f"vr/{id}")
    soup = BeautifulSoup(tournamentInfo, "html.parser")

    eventName = soup.select_one("h3.mb-0.text-truncate.ps-5").get_text(strip=True)

    table = soup.select("table.table-bordered tr")
    for row in table:
        cells = row.find_all("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)

            if label.lower() in ["città", "city"]:
                location = cells[1].get_text(strip=True)
            elif label.lower() in ["inizio - fine", "start - end"]:
                startNEndTournament = cells[1].get_text(strip=True)

    tournaments = []
    tournamentsTable = soup.select(".accordion-item")
    for item in tournamentsTable:
        name = item.select_one(".accordion-button span").get_text(strip=True)
        body = item.select_one(".accordion-body")

        playersLink = None
        resultsLink = None
        endRegistration = None

        for p in body.find_all("p"):
            if "Chiusura registrazioni" in p.text or "Registration expire" in p.text:
                endRegistration = p.text.split(": ", 1)[1]

        for a in body.find_all("a"):
            if "Giocatori" in a.text or "Players" in a.text:
                playersLink = a.get("href")
            elif "Risultati" in a.text or "Results" in a.text:
                resultsLink = a.get("href") if a.get("href") != "#" else None

        tournaments.append({
            "name": name,
            "endRegistration": endRegistration,
            "playersLink": playersLink,
            "resultsLink": resultsLink
        })

    return {
        "eventName": eventName,
        "location": location,
        "startNEndTournament": startNEndTournament,
        "tournaments": tournaments
    }

async def getPlayers(logInt: logger, event: dict) -> Optional[Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]]:
    modifiedEvent = False
    nameParts = settings.queryName.split()

    for tournament in event["tournaments"]:
        tournament["playersList"] = []
        tournament["playersResultList"] = []

        if tournament["playersLink"] != None:
            tournamentPlayers = await request(logInt, f"vr/{tournament["playersLink"]}")
            soup = BeautifulSoup(tournamentPlayers, "html.parser")

            rows = soup.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    playerName = cells[1].get_text(strip=True)
                    nameRegex = r"\b" + r".*?".join(re.escape(part) for part in nameParts) + r"\b"
                    if re.search(nameRegex, playerName, re.IGNORECASE):
                        if not modifiedEvent:
                            modifiedEvent = True
                        tournament["playersList"].append(playerName)

        if tournament["resultsLink"] != None:
            tournament["resultsLink"] = tournament["resultsLink"].lstrip("../")
            if tournament["resultsLink"].startswith("orion-trn/"):
                await logInt.error(f"In: https://www.vegaresult.com/{tournament["resultsLink"]} uses orion that is not supported yet")
                continue
            tournamentResults = await request(logInt, tournament["resultsLink"])
            soup = BeautifulSoup(tournamentResults, "html.parser")
            rows = soup.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    playerName = cells[1].get_text(strip=True)
                    nameRegex = r"\b" + r".*?".join(re.escape(part) for part in nameParts) + r"\b"
                    if re.search(nameRegex, playerName, re.IGNORECASE):
                        if not modifiedEvent:
                            modifiedEvent = True
                        tournament["playersResultList"].append(playerName)

    if modifiedEvent:
        return event

    return

async def query(logInt: logger) -> List[Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]]:

    ids = await getIds(logInt)

    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(getTournamentInfo(logInt, id)) for id in ids]
    results = [task.result() for task in tasks]
    
    tasks = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(getPlayers(logInt, result)) for result in results]
    results = [task.result() for task in tasks]
    results = [result for result in results if result is not None]

    return results
