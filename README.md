# TNcontrol

> [!WARNING]
> This software is unfinished. Keep your expectations low.

TNcontrol aims to find chess tournaments where the person you are looking for has pre-registered.

## How it works?

TNcontrol currently works by searching all Italian chess tournaments on [Vesus](https://vesus.org/) and also has support for checking if the person you are looking for has qualified for [CIGU18](https://it.wikipedia.org/wiki/Campionato_italiano_giovanile_di_scacchi).

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
$ python3 .\main.py --name=stefan --engine=VES --region=LAZ,CAL
$ # This command will search only on vesus all the people that contain stefan in the name in the regions of lazio and calabria
```
