import datetime
import asyncio

from typing import Optional, List, Dict
from src.logNSet import settings, engineFlags, logger, REGIONS
from src.engine import engine

class logBUI(logger):

    @classmethod
    async def error(cls, msg: str, shouldExit: bool = False, timestamp: Optional[str] = None) -> None:
        
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{timestamp}] ERROR: {msg}")

        await super().error(msg, shouldExit = shouldExit, timestamp = timestamp)
        return

def printResult(result: List[List[Optional[Dict[str, Dict[str, str | List[str]]]] | List[str]]]) -> None:

    outputStr = ""

    if settings.selectedEngine & engineFlags.VESUS:
        outputStr = f"Using the keyword: `{settings.queryName}` for seeing the Vesus pre-registrations, I found the following tournaments:\n\n"
        vesusResult = result[0]

        for tournament in vesusResult:
            for shortKey in tournament:
                outputStr += f"Tournament Name: {tournament[shortKey]['tornument']}\n"
                outputStr += f" Place: {tournament[shortKey]['location']}\n"
                outputStr += f" End of registration: {tournament[shortKey]['endRegistration']}\n"
                outputStr += f" Start of tournament: {tournament[shortKey]['startTornument']}\n"
                outputStr += f" Tournament Link: https://www.vesus.org/tournament/{shortKey}\n"
                outputStr += f" Who There:\n"
                for names in tournament[shortKey]["name"]:
                    outputStr += f"  - {names}\n"
                outputStr += "\n"
    
    if settings.selectedEngine & engineFlags.CIGU18:
        
        if settings.selectedEngine & engineFlags.VESUS: GIGResult = result[1]
        else: GIGResult = result[0]

        outputStr += f"Using the keyword: `{settings.queryName}` in the qualified CIGU18 FSI database, I found:\n"

        for quialified in GIGResult:
           outputStr += "\n"
           outputStr += f"Name: {quialified[1]}\n"
           outputStr += f" Region: {quialified[5]}\n"
           outputStr += f" Province: {quialified[4]}\n"
           outputStr += f" Birthdate: {quialified[2]}\n"
           outputStr += f" Sex: {quialified[6]}\n"
           outputStr += f" FSI ID: {quialified[0]}\n"
           outputStr += f" Club ID: {quialified[3]}\n"
    
    print(outputStr, end="")
    return

def main() -> None:

    if settings.queryName == "":
        print("Select the name to query...")
        settings.queryName = input("> ")

        if settings.queryName == "":
            print("Please select a name to query...")
            exit(-1)

    if settings.vesusRegionsToQuery == [] or settings.vesusRegionsToQuery == [""]:
        for region in REGIONS.keys():
            settings.vesusRegionsToQuery.append(region)


    result = asyncio.run(engine.start(logBUI()))
    printResult(result)
    
    return