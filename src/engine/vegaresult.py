#!/usr/bin/python3
# WARNING: The vegaresult engine does not have the basic functionality yet so it is not yet merged with tncontrol engines manager but it can be run as a standalone script
# when it reaches a semi-functional state it can be executed by tncontrol
import requests
import json


def main() -> None:
    
    url = "https://www.vegaresult.com/vr/"

    r = requests.get(url + "get_tournaments.php?status=next&timecontrol=all&interest=all&type=all&event=&startdate=&enddate=")
    data = json.loads(r.text)["tournaments"]

    ids = []

    for tornament in data:
        ids.append(tornament["id"])
    
    print(ids)
    return 

if __name__ == "__main__":
    main()