import aiohttp
import csv
import io
import re

from typing import List
from src.logNSet import settings, logger

async def query(logInt: logger) -> List[List[str]]:
    url = "https://www.federscacchi.it/giova/finalisti.php?azione=2"
    qualified = []
    text = None

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=180)) as response:
            if response.status < 200 or response.status > 299:
                text = await response.text()
                await logInt.error(f"UNEXPECTED STATUS CODE: {response.status}\n{text}", shouldExit=True)
                
            text = await response.text()

    parsedText = csv.reader(io.StringIO(text), delimiter=";")
    nameParts = re.split(r'\s+', settings.queryName.strip().lower())

    for row in parsedText:
        playerName = row[1].lower()

        if all(re.search(re.escape(part), playerName, re.IGNORECASE) for part in nameParts):
            qualified.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])

    await logInt.apiRequest(url, {}, text)
    return qualified