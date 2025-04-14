from src.logNSet import settings, interfaces, loadSettings
from src.interfaces import args
from src.interfaces import basicUI
from src.interfaces import telegram

def main() -> None:

    args.parseArgs()
    loadSettings()

    if settings.interface == interfaces.BASIC_UI:
        basicUI.main()
    elif settings.interface == interfaces.TELEGRAM:
        telegram.main()
    
    return
