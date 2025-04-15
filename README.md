# TNcontrol

> [!WARNING]
> This software is unfinished. Keep your expectations low.

TNcontrol is a tool designed to find chess tournaments where the person you are looking for has pre-registered. It supports querying on [Vesus](https://vesus.org/) and checks if the person you are looking for has qualified for [CIGU18](https://it.wikipedia.org/wiki/Campionato_italiano_giovanile_di_scacchi), and it also integrates with Telegram for easier interaction.

---

## Features

- Search for italian chess tournaments on [Vesus](https://vesus.org/).
- Check if a person has qualified for [CIGU18](https://it.wikipedia.org/wiki/Campionato_italiano_giovanile_di_scacchi).
- Support for querying specific Italian regions for vesus.
- Command-line interface.
- Telegram bot integration for interactive usage.
- Toggle between engines (Vesus and CIGU18).
- Logging system for tracking errors and operations.
- Supports a setting file to make persistent queries without entering data every time

- Daily automatic notifications (planned).
- Proxy support (planned).
- Improved TUI (Text User Interface) for better interaction (planned).

---

## Quick Start

### Install dependencies

```console
$ pip install -r requirements.txt
```

### Basic usage

```console
$ python3 ./main.py
```

And follow the instructions of the cli.

### "Advanced" usage

If you want to have more granularity on TNcontrol you can use the command arguments to select if you want to query only on CIGU18 or on Vesus or you can select the Italian regions on which to query

```console
$ python3 ./main.py --name=stefan --engine=VES --region=LAZ,CAL
# This command will search only on vesus all the people that contain stefan in the name in the regions of lazio and calabria
```

If you want to use TNcontrol with the telegram interface just create a bot with [@BotFather](https://telegram.me/BotFather) and take the key then pass this command to the server

```console
$ python3 ./main.py --telegram=YOUR_API_KEY_GOES_HERE
```

You can also create a settings.json file in the program root to keep your settings.
```json
{
    // IMPORTANT! Json does not support comments I am putting them for documentation but in real usage it will not work

    // here goes the interface you want to use with TNcontrol it can be 'basicUI' for the cli interface or 'telegram' to interface as a telegram bot
    "interface": "telegram",
    // If you specify telegram interface you will have to enter the key here
    "telegramKey": "YOUR_API_KEY_GOES_HERE",
    // Here enter the person you want to perform the query
    "queryName": "stefan",
    // Here you can select which engine(s) to use and you can use this notation but also the notation of '--available-engines'
    "selectedEngine": ["vesus", "cigu18"],
    // Here if you are using the vesus and you do not want to search for all the tournaments in italy you can specify the regions where you want to make the query with the notation '--available-regions'
    "vesusSelectedRegions": ["LAZ", "CAL"]
}
```

---

## TODO

- For the engine
    [ ] Add a flag to disable logs
    [ ] Add syntax to query multiple people
    [ ] Add support to query [Vegaresult](https://www.vegaresult.com/it/tournaments.php)
    [ ] Add proxy support so ip address doesn't timeout


- For the telegram interface
    [ ] Add support for the '--region' flag
    [ ] Add support for doing an automatic query every day at a selectable time

- For the terminal interface
    [ ] Improve the cli and program argument parameters
    [ ] Add support to a tui interface