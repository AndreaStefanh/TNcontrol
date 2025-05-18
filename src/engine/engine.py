import asyncio

from typing import Union, Dict, List
from src.logNSet import settings, engineFlags, logger
from src.engine import vesus
from src.engine import vegaresult
from src.engine import CIGU18

async def start(logInt: logger) -> List[List[Union[List[Dict[str, Union[str, Dict[str, str], Dict[str, List[str]]]]], List[Dict[str, Union[str, List[Dict[str, Union[str, List[str]]]]]]], List[List[Union[str, int]]]]]]:

    tasks = []
    async with asyncio.TaskGroup() as tg:
        if settings.selectedEngine & engineFlags.VESUS:         tasks.append(tg.create_task(vesus.query(logInt)))
        if settings.selectedEngine & engineFlags.VEGARESULT:    tasks.append(tg.create_task(vegaresult.query(logInt)))
        if settings.selectedEngine & engineFlags.CIGU18:        tasks.append(tg.create_task(CIGU18.query(logInt)))
    result = [task.result() for task in tasks]

    return result