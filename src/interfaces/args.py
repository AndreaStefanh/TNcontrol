import sys

from src.logNSet import engineFlags, settings, REGIONS

def parseArgs():

    sys.argv.pop(0)
    
    for arg in sys.argv:
        arg = arg.lower()
        
        if arg == "-h" or arg == "--help":
            print("Usage: python3 tncontrol.py [options]")
            print("Options:")
            print("  -h, --help                 Show this help message and exit")
            print("      --name=<NAME>          Set the to perform the query on")
            print("      --engine=<ENG>         Select one or more engines separated by commas to perform the query")
            print("      --region=<REG | ALL>   Select one or more regions separated by commas to perform the query for the vesus engine")
            print("                             (default all enabled --region=ALL)")
            print("      --available-engines    Show all available engines")
            print("      --available-regions    Show all available regions formart for the '--region' flag")
            # TODO: Add parameters disable logging and load settings from file
            exit(0)

        elif arg.startswith("--name="):
            name = arg.split("=")[1]

            if name == "":
                print("Error: '--name=' cannot be empty")
                exit(-1)
            
            settings.queryName = name
            
        elif arg.startswith("--engine="):
            engines = arg.split("=")[1].split(",")

            if engines == [""]:
                print("Error: '--engine=' cannot be empty")
                exit(-1)

            settings.selectedEngine = engineFlags.NONE

            for engine in engines:
                match engine:
                    case "ves": settings.selectedEngine |= engineFlags.VESUS
                    case "cig": settings.selectedEngine |= engineFlags.CIGU18
                    case _: print(f"Error: '{engine}' is not a valid engine"); exit(-1)
            
        elif arg.startswith("--region="):
            regions = arg.split("=")[1].split(",")

            if regions == [""]:
                print("Error: '--region=' cannot be empty")
                exit(-1)
            
            for region in regions:
                if region == "all":
                    settings.vesusRegionsToQuery = list(REGIONS.keys())
                    break
                elif region.upper() in REGIONS.values():
                    settings.vesusRegionsToQuery.append(list(REGIONS.keys()) [list(REGIONS.values()).index(region.upper())])
                else:
                    print(f"Error: '{region}' is not a valid region")
                    exit(-1)
        
        elif arg == "--available-engines":
            print("Available engines:")
            print("VES  -> VESUS")
            print("CIG  -> CIGU18")
            exit(0)

        elif arg == "--available-regions":
            print("Available regions fromat for the '--region' flag:")
            for region, code in REGIONS.items():
                print(f"{code}  -> {region}")
            exit(0)
    
    return