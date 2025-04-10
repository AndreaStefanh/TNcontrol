import asyncio

from typing import Dict, List, Optional
from src.logNSet import settings, engineFlags, logger
from src.engine import vesus
from src.engine import CIGU18

async def start(logInt: logger) -> List[List[Optional[Dict[str, Dict[str, str | List[str]]]] | List[str]]]:

    tasks = []
    async with asyncio.TaskGroup() as tg:
        if settings.selectedEngine & engineFlags.VESUS:  tasks.append(tg.create_task(vesus.query(logInt)))
        if settings.selectedEngine & engineFlags.CIGU18: tasks.append(tg.create_task(CIGU18.query(logInt)))
    result = [task.result() for task in tasks]

    return result