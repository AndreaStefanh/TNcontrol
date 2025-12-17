# TNcontrol

> [!WARNING]
> This software is unfinished. Keep your expectations low.

TNcontrol is a tool designed to find chess tournaments where the person you are looking for has pre-registered. It supports querying on [Vesus](https://vesus.org/), on [Vegaresult](https://www.vegaresult.com/it/tournaments.php) and checks if the person you are looking for has qualified for [CIGU18](https://it.wikipedia.org/wiki/Campionato_italiano_giovanile_di_scacchi), and it also integrates with Telegram for easier interaction.

---

## Demo

Telegram interface, basic demo.

![Demo](https://github.com/user-attachments/assets/cd19156e-6128-4d0c-bca9-445dde20cd25)

---

## Features

- Search for italian chess tournaments on [Vesus](https://vesus.org/) and on [Vegaresult](https://www.vegaresult.com/it/tournaments.php).
- Check if a person has qualified for [CIGU18](https://it.wikipedia.org/wiki/Campionato_italiano_giovanile_di_scacchi).
- Support for querying specific Italian regions for vesus.
- Supports querying multiple people by separating names with '|' symbol
- Command-line interface.
- Telegram bot integration for interactive usage.
- Toggle between engines (Vesus and CIGU18).
- Logging system for tracking errors and operations.
- Supports a setting file to make persistent queries without entering data every time
- Supports in the Telegram interface a feature to run an automatic daily query at a selectable time

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

If you want to have more granularity in your settings:

```console
$ python3 ./main.py --advanced
```

And follow the instructions of the cli.

---

Or you can use the command arguments:

```console
$ python3 ./main.py --name=stefan --engine=VES --region=LAZ,CAL
# This command will search only on vesus all the people that contain stefan in the name in the regions of lazio and calabria
```

---

If you want to make a multiple query you can separate the names with the '|' operator.

You can use the '|' operator everywhere and it is possible to insert the name of the person you want to query (in the cli, in the argument parameters and on telegram).

```console
$ python3 ./main.py --name="stefan andrea|sonis francesco"
```

---

If you want to use TNcontrol with the telegram interface just create a bot with [@BotFather](https://telegram.me/BotFather) and take the key then pass this command to the server

```console
$ python3 ./main.py --telegram=YOUR_API_KEY_GOES_HERE
```

---

You can also create a **settings.json** file in the program root to keep your settings.
```json5
{
  // here goes the interface you want to use with TNcontrol it can be 'basicUI' for 
  // the cli interface or 'telegram' to interface as a telegram bot (default is basicUI)
  "interface": "telegram",

  // If you specify telegram interface you will have to enter the key here
  "telegramKey": "YOUR_API_KEY_GOES_HERE",
    
  // If you have selected the telegram interface then activate the automated run feature from here
  // (default is false)
  "telegramAutoRun": true,
    
  // Here you can enter the time in UTC to perform automated run (default is 19:00 UTC)
  "autoRunTime": "21:00",
    
  // Here enter the person you want to perform the query
  "queryName": "stefan",
    
  // Here you can select which engine(s) to use and you can use this notation
  // but also the notation of '--available-engines' (default are both)
  "selectedEngine": ["vesus", "cigu18"],
    
  // Here if you are using the vesus and you do not want to search for all the tournaments in italy 
  // you can specify the regions where you want to make the query with the notation 
  // '--available-regions' (default are all of them)
  "vesusSelectedRegions": ["LAZ", "CAL"],
    
  // Enable all logging on API requests in the apiLogs.txt file as the '-l' argument flag 
  // (default is false)
  "logApiRequests": true
}
```

---

## Known Problems

- Sometimes connections to Vesus fail to perform the initial 3-way TCP handshake (no idea why)
- If you make many queries on vesus if you have especially all the regions selected without at least waiting 1 minute between one request and another the vesus server will timeout your ip
- CIGU18 engine takes 30 seconds to run when vesus only takes 10 seconds to run for all regions so cig engine creates a 20 second bottleneck because [F.S.I.](https://en.wikipedia.org/wiki/Italian_Chess_Federation) servers suck
- The docIDs for Vesus parsing will need to be updated from time to time

---

## TODO

- [ ] Add proxy support so ip address doesn't timeout
- [ ] Add support to a tui interface
