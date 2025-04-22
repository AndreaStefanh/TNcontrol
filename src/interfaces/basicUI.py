import prompt_toolkit
import datetime
import calendar
import asyncio

from prompt_toolkit.history import DummyHistory
from typing import Optional, Union, List, Dict
from src.logNSet import settings, engineFlags, logger, REGIONS, PROVINCE
from src.engine import engine

class logBUI(logger):

    @classmethod
    async def error(cls, msg: str, shouldExit: bool = False, timestamp: Optional[str] = None) -> None:
        
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{timestamp}] ERROR: {msg}")

        await super().error(msg, shouldExit = shouldExit, timestamp = timestamp)
        return

def takeInput() -> str:
    try:
        selection = prompt_toolkit.prompt("> ", history = DummyHistory())
    except KeyboardInterrupt:
        exit(0)
    
    return selection

def printResult(result: Union[List[Dict[str, Dict[str, Union[str, List[str]]]]], List[List[str]]]) -> None:

    outputStr = ""

    if settings.selectedEngine & engineFlags.VESUS:
        outputStr = f"Using the keyword: `{settings.queryName}` for seeing the Vesus pre-registrations, I found the following tournaments:\n\n"
        vesusResult = result[0]

        if len(vesusResult) >= 1:
            for tournament in vesusResult:
                for shortKey in tournament:
                    outputStr += f"Tournament Name: {tournament[shortKey]['tournament']}\n"
                    outputStr += f" Place: {tournament[shortKey]['location']}\n"
                    outputStr += f" End of registration: {datetime.datetime.fromisoformat(tournament[shortKey]['endRegistration'].replace("Z", "+00:00")).strftime("%d %B %Y, %H:%M")} UTC\n"
                    outputStr += f" Start of tournament: {datetime.datetime.fromisoformat(tournament[shortKey]['startTournament'].replace("Z", "+00:00")).strftime("%d %B %Y, %H:%M")} UTC\n"
                    outputStr += f" Tournament Link: https://www.vesus.org/tournament/{shortKey}\n"
                    outputStr += f" Who There:\n"
                    for names in tournament[shortKey]["names"]:
                        outputStr += f"  - {names}\n"
                    outputStr += "\n"
        else:
            outputStr += "Couldn't find anything in vesus engine\n\n"
    
    if settings.selectedEngine & engineFlags.CIGU18:
        
        if settings.selectedEngine & engineFlags.VESUS: GIGResult = result[1]
        else: GIGResult = result[0]

        outputStr += f"Using the keyword: `{settings.queryName}` in the qualified CIGU18 FSI database, I found:\n"

        if len(GIGResult) >= 1:
            for quialified in GIGResult:
                outputStr += "\n"
                outputStr += f"Name: {quialified[1]}\n"

                for k, v in REGIONS.items():
                    if v == quialified[5]:
                        outputStr += f" Region: {k}\n"
                        break
                #outputStr += f" Region: {quialified[5]}\n"

                outputStr += f" Province: {PROVINCE[quialified[4]]}\n"
                bdate = quialified[2].split("-")
                outputStr += f" Birthdate: {bdate[2]} {calendar.month_name[int(bdate[1])]} {bdate[0]}\n"
                outputStr += f" Sex: {"Male" if quialified[6] == "M" else "Female"}\n"
                outputStr += f" FSI ID: {quialified[0]}\n"
                outputStr += f" FSI Info: https://www.federscacchi.com/fsi/index.php/struttura/tesserati?&idx={quialified[0]}&ric=1\n"
                outputStr += f" Club ID: {quialified[3]}\n"
                outputStr += f" Club Info: https://www.federscacchi.com/fsi/index.php/struttura/societa?idx={quialified[3]}&anno={datetime.datetime.now().year}&ric=1\n"
        else:
            outputStr += "\nCouldn't find anything in CIGU18 engine\n\n"
    
    print(f"\r{outputStr}", end="", flush=True)
    return

def main() -> None:

    if settings.queryName == "":
        print("Select the name to query...")
        settings.queryName = takeInput()

        if settings.queryName == "":
            print("Please select a name to query...")
            exit(-1)

    if settings.advancedMode is True:
        
        print("Select where you want to execute the query by indicating the corresponding number (empty for both)")
        print("1. Vesus")
        print("2. CIGU18")
        selection = takeInput()

        if selection == "1":
            settings.selectedEngine = engineFlags.VESUS
        elif selection == "2":
            settings.selectedEngine = engineFlags.CIGU18
        elif selection == "":
            pass
        else:
            print(f"ERROR: '{selection}' isn't a valid answer")
            exit(-1)
        
        if settings.selectedEngine & engineFlags.VESUS:
            print("Select the regions in which to perform the vesus query by indicating the corresponding number separating them with spaces (empty for all)")
            for i, region in enumerate(REGIONS.keys(), start = 1):
                print(f"{i}. {region}")
            
            selection = takeInput().split(" ")
            for i in selection:

                if i != "":
                    try:
                        i = int(i)
                    except ValueError:
                        print(f"ERROR: '{i}' isn't a valid answer")
                        exit(-1)

                    if i > 20 or i < 1:
                        print(f"ERROR: '{i}' isn't a valid answer")
                        exit(-1)

                    settings.vesusRegionsToQuery.append(list(REGIONS.keys())[i - 1])
        
        print("Do you wanna log requests on the API? [y/N]")
        selection = takeInput().lower()

        if selection == "y":
            settings.logApiRequests = True
        elif selection == "n" or selection == "":
            settings.logApiRequests = False
        else:
            print(f"ERROR: '{selection}' isn't a valid answer")
            exit(-1)


    if settings.vesusRegionsToQuery == [] or settings.vesusRegionsToQuery == [""]:
        for region in REGIONS.keys():
            settings.vesusRegionsToQuery.append(region)

    print("Loading...", end="", flush=True)

    result = asyncio.run(engine.start(logBUI()))
    printResult(result)
    
    return