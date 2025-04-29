#!/usr/bin/python3
# WARNING: The vegaresult engine does not have the basic functionality yet so it is not yet merged with tncontrol engines manager but it can be run as a standalone script
# when it reaches a semi-functional state it can be executed by tncontrol
import requests
import json
from bs4 import BeautifulSoup

def request(param: str) -> str:
    r = requests.get("https://www.vegaresult.com/vr/" + param)
    return r.text

def getIds() -> list[str]:
    tournamentsInfo = request("get_tournaments.php?status=next&timecontrol=all&interest=all&type=all&event=&startdate=&enddate=")
    tournamentsInfo = json.loads(tournamentsInfo)["tournaments"]

    ids = []
    for tornament in tournamentsInfo:
        ids.append(tornament["id"])
    
    return ids

def getEventId() -> None:

    ids = getIds()
    for id in ids:
        tournamentPage = request(id)
        soup = BeautifulSoup(tournamentPage, "html.parser")
        
        for link in soup.find_all('a'):
            if link.get("href").startswith("players.php?section_id="):
                print(link.get("href"))
    
    return

def main() -> None:
    
    getEventId()
    return 

if __name__ == "__main__":
    main()