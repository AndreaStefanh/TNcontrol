import prompt_toolkit
import datetime
import calendar
import asyncio
import sys

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
        sys.exit(0)
    
    return selection

def printResult(result: List[List[Union[List[Dict[str, Union[str, Dict[str, str], Dict[str, List[str]]]]], List[Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]], List[List[Union[str, int]]]]]]) -> None:
    names = settings.queryName.split("|")
    if len(names) == 1:
        formattedNames = f"`{names[0].strip()}`"
    else:
        formattedNames = ", ".join([f"`{name.strip()}`" for name in names])
    outputStr = ""

    if settings.selectedEngine & engineFlags.VESUS:
        outputStr += f"Using the keyword(s): {formattedNames} for Vesus pre-registrations, I found the following tournaments:\n\n"
        vesusResult = result[0]

        if len(vesusResult) >= 1:
            for tournament in vesusResult:
                outputStr += f"Event Name: {tournament['eventName']}\n"
                outputStr += f" Location: {tournament['location']}\n"
                outputStr += f" End of Registration:     {datetime.datetime.fromisoformat(tournament['endRegistration'].replace('Z', '+00:00')).strftime('%d %B %Y, %H:%M')} UTC\n"
                outputStr += f" Start of the Tournament: {datetime.datetime.fromisoformat(tournament['startTournament'].replace('Z', '+00:00')).strftime('%d %B %Y, %H:%M')} UTC\n"
                outputStr += f" End of the Tournament:   {datetime.datetime.fromisoformat(tournament['endTournament'].replace('Z', '+00:00')).strftime('%d %B %Y, %H:%M')} UTC\n"
                outputStr += f" Participants:\n"
                for group, participants in tournament["names"].items():
                    shortKey = next(key for key, value in tournament["shortkeys"].items() if value == group)
                    outputStr += f"  {group} (Link: https://www.vesus.org/tournament/{shortKey}):\n"

                    for participant in participants:
                        outputStr += f"    - {participant}\n"
                outputStr += "\n"
        else:
            outputStr += "Couldn't find anything in Vesus engine.\n\n"

    if settings.selectedEngine & engineFlags.VEGARESULT:
        outputStr += f"Using the keyword(s): {formattedNames} for Vegaresult pre-registrations, I found the following tournaments:\n\n"
        if settings.selectedEngine & engineFlags.VESUS: 
            vegares = result[1]
        else:
            vegares = result[0]
        
        if len(vegares) >= 1:
            for event in vegares:
                outputStr += f"Event Name: {event['eventName']}\n"
                outputStr += f" Location: {event['location']}\n"
                
                dates = event["startNEndTournament"].split("-")
                outputStr += f" Start of the Event: {dates[0]}\n"
                outputStr += f" End of the Event:  {dates[1]}\n"
                
                outputStr += f" Tournaments:\n"
                for tournament in event["tournaments"]:
                    
                    if tournament["playersList"] == [] and tournament["playersResultList"] == []:
                        continue

                    outputStr += f"  Tournament Name: {tournament["name"]}\n"
                    
                    if tournament["endRegistration"] != None:
                        outputStr += f"  End of Registration: {datetime.datetime.strptime(tournament["endRegistration"], "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y, %H:%M")}\n"
                    
                    if tournament["playersList"] != []:
                        outputStr += f"   From players tab (Link: https://www.vegaresult.com/vr/{tournament["playersLink"]}):\n"
                        for player in tournament["playersList"]:
                            outputStr += f"    - {player}\n"
                                        
                    if tournament["playersResultList"] != []:
                        outputStr += f"   From results tab (Link: https://www.vegaresult.com/{tournament["resultsLink"]}):\n"
                        for player in tournament["playersResultList"]:
                            outputStr += f"    - {player}\n"
                    
                outputStr += "\n"
        else:
            outputStr += "Couldn't find anything in Vegaresult engine.\n\n"

    if settings.selectedEngine & engineFlags.CIGU18:
        outputStr += f"Using the keyword(s): {formattedNames} in the qualified CIGU18 FSI database, I found:\n"
        if settings.selectedEngine & engineFlags.VESUS and settings.selectedEngine & engineFlags.VEGARESULT:
            cigResult = result[2]
        elif settings.selectedEngine & engineFlags.VESUS or settings.selectedEngine & engineFlags.VEGARESULT:
            cigResult = result[1]
        else:
            cigResult = result[0]

        if len(cigResult) >= 1:
            for qualified in cigResult:
                outputStr += "\n"
                outputStr += f"Name: {qualified[1]}\n"
                outputStr += f" Region: {next(k for k, v in REGIONS.items() if v == qualified[5])}\n"
                outputStr += f" Province: {PROVINCE[qualified[4]]}\n"
                bdate = qualified[2].split("-")
                outputStr += f" Birthdate: {bdate[2]} {calendar.month_name[int(bdate[1])]} {bdate[0]}\n"
                outputStr += f" Sex: {"Male" if qualified[6] == "M" else "Female"}\n"
                outputStr += f" FSI ID: {qualified[0]}\n"
                outputStr += f" FSI Info: https://www.federscacchi.com/fsi/index.php/struttura/tesserati?&idx={qualified[0]}&ric=1\n"
                outputStr += f" Club ID: {qualified[3]}\n"
                outputStr += f" Club Info: https://www.federscacchi.com/fsi/index.php/struttura/societa?idx={qualified[3]}&anno={datetime.datetime.now().year}&ric=1\n"
        else:
            outputStr += "\nCouldn't find anything in CIGU18 engine.\n\n"

    print(f"\r{outputStr}", end="", flush=True)
    return

def main() -> None:

    if settings.queryName == "":
        print("Select the name to query...")
        settings.queryName = takeInput()

        if settings.queryName == "":
            print("Please select a name to query...")
            sys.exit(-1)

    if settings.advancedMode is True:
        
        print("Select where you want to execute the query by indicating the corresponding number separated by spaces (empty for all)")
        print("1. Vesus")
        print("2. Vegaresult")
        print("3. CIGU18")
        selections = takeInput().split()

        if selections != []:
            settings.selectedEngine = engineFlags.NONE

            for selection in selections: 
                if selection == "1":
                    settings.selectedEngine |= engineFlags.VESUS
                elif selection == "2":
                    settings.selectedEngine |= engineFlags.VEGARESULT
                elif selection == "3":
                    settings.selectedEngine |= engineFlags.CIGU18
                elif selection == "":
                    settings.selectedEngine = engineFlags.VESUS | engineFlags.VEGARESULT | engineFlags.CIGU18
                else:
                    print(f"ERROR: '{selection}' isn't a valid answer")
                    sys.exit(-1)
        
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
                        sys.exit(-1)

                    if i > 20 or i < 1:
                        print(f"ERROR: '{i}' isn't a valid answer")
                        sys.exit(-1)

                    settings.vesusRegionsToQuery.append(list(REGIONS.keys())[i - 1])
        
        print("Do you wanna log requests on the API? [y/N]")
        selection = takeInput().lower()

        if selection == "y":
            settings.logApiRequests = True
        elif selection == "n" or selection == "":
            settings.logApiRequests = False
        else:
            print(f"ERROR: '{selection}' isn't a valid answer")
            sys.exit(-1)


    if settings.vesusRegionsToQuery == [] or settings.vesusRegionsToQuery == [""]:
        for region in REGIONS.keys():
            settings.vesusRegionsToQuery.append(region)

    print("Loading...", end="", flush=True)

    result = asyncio.run(engine.start(logBUI()))
    printResult(result)
    
    return