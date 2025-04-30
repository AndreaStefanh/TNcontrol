#!/usr/bin/python3
# WARNING: The vegaresult engine does not have the basic functionality yet so it is not yet merged with tncontrol engines manager but it can be run as a standalone script
# when it reaches a semi-functional state it can be executed by tncontrol
import asyncio
import aiohttp
import json

from bs4 import BeautifulSoup

async def request(param: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.vegaresult.com/vr/" + param, timeout=aiohttp.ClientTimeout(total=180)) as response:

            if response.status != 200:
                text = await response.text()
                print(f"UNEXPECTED STATUS CODE: {response.status} WHILE QUERYNG: https://www.vegaresult.com/vr/{param}\n{text}")
                exit(-1)

            return await response.text()

async def getIds() -> list[str]:
    tournamentsInfo = await request("get_tournaments.php?status=next&timecontrol=all&interest=all&type=all&event=&startdate=&enddate=")
    tournamentsInfo = json.loads(tournamentsInfo)["tournaments"]

    ids = []
    for tornament in tournamentsInfo:
        ids.append(tornament["id"])
    
    return ids

async def getTournamentInfo(id: str) -> dict:
    tournamentInfo = await request(id)
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
        for a in body.find_all("a"):
            if "Giocatori" in a.text or "Players" in a.text:
                playersLink = a.get("href")
            elif "Risultati" in a.text or "Results" in a.text:
                resultsLink = a.get("href") if a.get("href") != "#" else None

        tournaments.append({
            "name": name,
            "playersLink": playersLink,
            "resultsLink": resultsLink
        })

    return {
        "eventName": eventName,
        "location": location,
        "startNEndTournament": startNEndTournament,
        "tournaments": tournaments
    }

async def main() -> None:
    ids = await getIds()

    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(getTournamentInfo(id)) for id in ids]
    results = [task.result() for task in tasks]
    
    for result in results:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
