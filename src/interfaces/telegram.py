import traceback
import datetime
import calendar
import asyncio
from typing import Optional
from enum import IntFlag
from apscheduler.jobstores.base import JobLookupError

from telegram import Bot, error, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from src.logNSet import settings, logger, engineFlags, REGIONS, PROVINCE
from src.engine import engine


class menuFlags(IntFlag):
    MAIN_MENU = 0
    QUERY_NAME = 1
    SELECT_ENGINE = 2
    SELECT_REGION_P1 = 3
    SELECT_REGION_P2 = 4
    SELECT_REGION_P3 = 5
    SELECT_REGION_P4 = 6
    AUTOMATED_RUN = 7
    SET_TIME = 8
selectedMenu: menuFlags = menuFlags.MAIN_MENU

app = None
bot = None
savedChatIDs = []
MAX_LENGTH = 4000

class logTG(logger):

    @classmethod
    async def error(cls, msg: str, shouldExit: bool = False, timestamp: Optional[str] = None, stacktrace: Optional[str] = None) -> None:
        
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if stacktrace is None:
            print(f"[{timestamp}] ERROR: {msg}")
        else:
            print(f"[{timestamp}] ERROR: {msg}\nSTACKTRACE:\n{stacktrace}")

        for chatID in savedChatIDs:
            try:
                msg = f"⚠️ [{timestamp}] ERROR: {msg}"
                for i in range(0, len(msg), MAX_LENGTH):
                    await bot.send_message(chat_id=chatID, text=msg[i:i+MAX_LENGTH])
            except error.TelegramError as e:
                errorDetails = traceback.format_exc()

                print(f"Failed to send error message to chat ID {chatID}: {e}.\nSee errorLogs file to see more informations")
                with open("errorLogs.txt", "a", encoding="utf-8") as logFile:
                    logFile.write(f"Failed to send error message to chat ID {chatID}: {e}\nSTACKTRACE:\n{errorDetails}\n")
        
        if stacktrace is not None:
            msg += f"\nSTACKTRACE:\n{stacktrace}"

        await super().error(msg, shouldExit = shouldExit, timestamp = timestamp)
        return


async def shutdown() -> None:
    global app
    
    if app is not None:
        await app.stop()
    
    #exit(0)

def loadChatID() -> None:
    global savedChatIDs

    try:
        with open("chatIDs.txt", "r", encoding="utf-8") as chatFile:
            for line in chatFile:
                savedChatIDs.append(line.strip())
    except FileNotFoundError:
        with open("chatIDs.txt", "w", encoding="utf-8") as chatFile:
            pass

    return

def saveChatID(chatID: str) -> None:
    global savedChatIDs

    if chatID not in savedChatIDs:
        with open("chatIDs.txt", "a", encoding="utf-8") as chatFile:
            chatFile.write(f"{chatID}\n")
            savedChatIDs.append(chatID)

    return

def splitMessage(message: str) -> list[str]:
    blocks = []
    start = 0
    lenght = len(message)
    
    while start < lenght:
        end = min(start + MAX_LENGTH, lenght)
        block = message[start:end]

        if end == lenght:
            blocks.append(block)
            break
        
        posNewLine = block.rfind('\n')
        if posNewLine != -1:
            blocks.append(block[:posNewLine + 1])
            start += posNewLine + 1
        else:
            blocks.append(block)
            start += MAX_LENGTH

    return blocks

def escapeMarkdown(message: str) -> str:
    escapeChars = ['*', '_', '[', ']', '`']
    for char in escapeChars:
        message = message.replace(char, f'\\{char}')
    
    return message

async def sendMsg(message: str, replyMarkup: Optional[ReplyKeyboardMarkup] = None) -> None:

    for chatID in savedChatIDs:
        if replyMarkup is None:
            await bot.send_message(chat_id = chatID, text = message, parse_mode = "markdown", disable_web_page_preview = True)
        else:
            await bot.send_message(chat_id = chatID, text = message, parse_mode = "markdown", disable_web_page_preview = True, reply_markup = replyMarkup)

    return

async def printMessageWithMenu(message: str) -> None:

    match selectedMenu:
        
        case menuFlags.MAIN_MENU:
            msgBlocks = splitMessage(message)

            if settings.selectedEngine & engineFlags.VESUS:
                for msg in msgBlocks:
                    await sendMsg(msg, ReplyKeyboardMarkup([["👤 Query", "⚙️ Engine", "🗺️ Select Regions"], ["🔁 Automated Run", "▶️ Run"]], resize_keyboard=True))
            else:
                for msg in msgBlocks:
                    await sendMsg(msg, ReplyKeyboardMarkup([["👤 Query", "⚙️ Engine"], ["🔁 Automated Run", "▶️ Run"]], resize_keyboard=True))

        case menuFlags.QUERY_NAME:
            await sendMsg(message, ReplyKeyboardMarkup([["⬅️ Back"]], resize_keyboard=True))
        
        case menuFlags.SELECT_ENGINE:
            buttons = []
            if settings.selectedEngine & settings.selectedEngine.VESUS:
                buttons.append(["✅ Vesus"])
            else:
                buttons.append(["❌ Vesus"])
            
            if settings.selectedEngine & settings.selectedEngine.CIGU18:
                buttons.append(["✅ CIGU18"])
            else:
                buttons.append(["❌ CIGU18"])
            buttons.append(["⬅️ Back"])
            
            await sendMsg(message, ReplyKeyboardMarkup(buttons, resize_keyboard=True))

        case menuFlags.SELECT_REGION_P1:
            buttonsFirstRow = []
            for region in list(REGIONS.keys())[:3]:
                if region in settings.vesusRegionsToQuery:
                    buttonsFirstRow.append(f"✅ {region}")
                else:
                    buttonsFirstRow.append(f"❌ {region}")
            
            buttonsSecondRow = []
            for region in list(REGIONS.keys())[3:6]:
                if region in settings.vesusRegionsToQuery:
                    buttonsSecondRow.append(f"✅ {region}")
                else:
                    buttonsSecondRow.append(f"❌ {region}")
            
            await sendMsg(message, ReplyKeyboardMarkup([buttonsFirstRow, buttonsSecondRow, ["⬅️ Back (Main Menu)", "➡️ Next Page (2/4)"]], resize_keyboard=True))

        case menuFlags.SELECT_REGION_P2:
            buttonsFirstRow = []
            for region in list(REGIONS.keys())[6:9]:
                if region in settings.vesusRegionsToQuery:
                    buttonsFirstRow.append(f"✅ {region}")
                else:
                    buttonsFirstRow.append(f"❌ {region}")
            
            buttonsSecondRow = []
            for region in list(REGIONS.keys())[9:12]:
                if region in settings.vesusRegionsToQuery:
                    buttonsSecondRow.append(f"✅ {region}")
                else:
                    buttonsSecondRow.append(f"❌ {region}")
            
            await sendMsg(message, ReplyKeyboardMarkup([buttonsFirstRow, buttonsSecondRow, ["⬅️ Back to 1° page", "➡️ Next Page (3/4)"]], resize_keyboard=True))

        case menuFlags.SELECT_REGION_P3:
            buttonsFirstRow = []
            for region in list(REGIONS.keys())[12:15]:
                if region in settings.vesusRegionsToQuery:
                    buttonsFirstRow.append(f"✅ {region}")
                else:
                    buttonsFirstRow.append(f"❌ {region}")
            
            buttonsSecondRow = []
            for region in list(REGIONS.keys())[15:18]:
                if region in settings.vesusRegionsToQuery:
                    buttonsSecondRow.append(f"✅ {region}")
                else:
                    buttonsSecondRow.append(f"❌ {region}")
            
            await sendMsg(message, ReplyKeyboardMarkup([buttonsFirstRow, buttonsSecondRow, ["⬅️ Back to 2° page", "➡️ Next Page (4/4)"]], resize_keyboard=True))

        case menuFlags.SELECT_REGION_P4:
            buttonsFirstRow = []
            for region in list(REGIONS.keys())[18:]:
                if region in settings.vesusRegionsToQuery:
                    buttonsFirstRow.append(f"✅ {region}")
                else:
                    buttonsFirstRow.append(f"❌ {region}")
            
            await sendMsg(message, ReplyKeyboardMarkup([buttonsFirstRow, ["⬅️ Back to 3° page"]], resize_keyboard=True))

        case menuFlags.AUTOMATED_RUN:
            buttonsFirstRow = ["🕓 Set time"]
            if settings.telegramAutoRun is True:
                buttonsFirstRow.append("✅ Feature is enable")
            else:
                buttonsFirstRow.append("❌ Feature is disable")
            
            await sendMsg(message, ReplyKeyboardMarkup([buttonsFirstRow, ["⬅️ Back"]], resize_keyboard=True))
        
        case menuFlags.SET_TIME:
            await sendMsg(message, ReplyKeyboardMarkup([["⬅️ Back"]], resize_keyboard=True))

        case _:
            await sendMsg("Command not recognized.")
            return

    return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global selectedMenu
    selectedMenu = menuFlags.MAIN_MENU

    saveChatID(str(update.message.chat_id))

    await printMessageWithMenu("Telegram bot interface for [TNcontrol](https://github.com/AndreaStefanh/TNcontrol)")
    return

async def runCommand(context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
    if settings.queryName == "":
        await printMessageWithMenu("⚠️ Please enter a query name before running the bot.")
        return
    
    if settings.selectedEngine == engineFlags.NONE:
        await printMessageWithMenu("⚠️ Please select at least one engine before running the bot.")
        return
    
    await sendMsg("⏳ Loading...")
         
    try:
        result = await engine.start(logTG())
    except Exception as e:
        errorDetails = traceback.format_exc()
        await logTG.error(f"Error while running the bot: {e}.\nSee errorLogs file to see more informations.", stacktrace = errorDetails)
        return
    
    msg = ""
          
    if settings.selectedEngine & engineFlags.VESUS:
        msg = f"Using the keyword: '{escapeMarkdown(settings.queryName)}' for seeing the Vesus pre-registrations, I found the following tournaments:\n\n"
        vesusResult = result[0]
           
        if len(vesusResult) >= 1:
            for tournament in vesusResult:
                for shortKey in tournament:
                    msg += f"🔹 *Tournament Name:* {escapeMarkdown(tournament[shortKey]['tournament'])}\n"
                    msg += f"📍 *Place:* {escapeMarkdown(tournament[shortKey]['location'])}\n"
                    msg += f"📅 *End of registration:* {datetime.datetime.fromisoformat(tournament[shortKey]['endRegistration'].replace("Z", "+00:00")).strftime("%d %B %Y, %H:%M")} UTC\n"
                    msg += f"🎯 *Start of tournament:* {datetime.datetime.fromisoformat(tournament[shortKey]['startTournament'].replace("Z", "+00:00")).strftime("%d %B %Y, %H:%M")} UTC\n"
                    msg += f"🔗 [Tournament Link](https://www.vesus.org/tournament/{shortKey})\n"
                    msg += f"👥 *Who There:*\n"
                    for names in tournament[shortKey]["names"]:
                        msg += f"  - {escapeMarkdown(names)}\n"
                    msg += "\n"
        else:
            msg += "Couldn't find anything in vesus engine\n\n"
               
    if settings.selectedEngine & engineFlags.CIGU18:
        if settings.selectedEngine & engineFlags.VESUS:
            GIGResult = result[1]
        else:
            GIGResult = result[0]
         
        msg += f"Using the keyword: '{escapeMarkdown(settings.queryName)}' in the qualified CIGU18 FSI database, I found:\n"
        
        if len(GIGResult) >= 1:
            for quialified in GIGResult:
                msg += "\n"
                msg += f"👤 *Name:* {escapeMarkdown(quialified[1])}\n"

                for k, v in REGIONS.items():
                    if v == quialified[5]:
                        msg += f"🗺️ *Region:* {escapeMarkdown(k)}\n"
                        break
                #msg += f" 🗺️ *Region:* {escapeMarkdown(quialified[5])}\n"

                msg += f"📍 *Province:* {escapeMarkdown(PROVINCE[quialified[4]])}\n"
                bdate = quialified[2].split("-")
                msg += f"🎂 *Birthdate:* {bdate[2]} {calendar.month_name[int(bdate[1])]} {bdate[0]}\n"
                msg += f"⚧️ *Sex:* {"Male" if escapeMarkdown(quialified[6]) == "M" else "Female"}\n"
                msg += f"🇮🇹 *FSI ID:* [{escapeMarkdown(quialified[0])}](https://www.federscacchi.com/fsi/index.php/struttura/tesserati?&idx={escapeMarkdown(quialified[0])}&ric=1)\n"
                msg += f"🏢 *Club ID:* [{escapeMarkdown(quialified[3])}](https://www.federscacchi.com/fsi/index.php/struttura/societa?idx={escapeMarkdown(quialified[3])}&anno={datetime.datetime.now().year}&ric=1)\n"
        else:
            msg += "\nCouldn't find anything in CIGU18 engine\n\n"
          
    await printMessageWithMenu(msg)

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global selectedMenu

    saveChatID(str(update.message.chat_id))

    if selectedMenu == menuFlags.MAIN_MENU:
        match update.message.text:

            case "👤 Query":
                selectedMenu = menuFlags.QUERY_NAME
                    
                output = ""
                if settings.queryName == "":
                    output = "ℹ️ The query name is empty.\n"
                else:
                    output = f"ℹ️ The query name is: {settings.queryName}\n"
                output += "Please enter the query name:"

                await printMessageWithMenu(output)
            
            case "⚙️ Engine":
                selectedMenu = menuFlags.SELECT_ENGINE

                await printMessageWithMenu("ℹ️ Current engine settings:")

            case "▶️ Run":
                await runCommand()

            case "🗺️ Select Regions":
                selectedMenu = menuFlags.SELECT_REGION_P1

                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 1:")
            
            case "🔁 Automated Run":
                selectedMenu = menuFlags.AUTOMATED_RUN

                await printMessageWithMenu("ℹ️ Current automated run settings")
                
            case _:
                await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")

    elif selectedMenu == menuFlags.QUERY_NAME:
        match update.message.text:

            case "⬅️ Back":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu")

            case _:
                settings.queryName = update.message.text
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu(f"ℹ️ Query name set to '{settings.queryName}'.")
    
    elif selectedMenu == menuFlags.SELECT_ENGINE:
        match update.message.text:

            case "✅ Vesus" | "❌ Vesus":
                settings.selectedEngine ^= engineFlags.VESUS
                await printMessageWithMenu("ℹ️ Vesus engine toggled.")

            case "✅ CIGU18" | "❌ CIGU18":
                settings.selectedEngine ^= engineFlags.CIGU18
                await printMessageWithMenu("ℹ️ CIGU18 engine toggled.")

            case "⬅️ Back":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu")

            case _:
                await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
    
    elif selectedMenu == menuFlags.SELECT_REGION_P1:
        match update.message.text:

            case "➡️ Next Page (2/4)":
                selectedMenu = menuFlags.SELECT_REGION_P2
                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 2:")

            case "⬅️ Back (Main Menu)":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu")
            
            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.")
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.")
        
    elif selectedMenu == menuFlags.SELECT_REGION_P2:
        match update.message.text:

            case "➡️ Next Page (3/4)":
                selectedMenu = menuFlags.SELECT_REGION_P3
                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 3:")

            case "⬅️ Back to 1° page":
                selectedMenu = menuFlags.SELECT_REGION_P1
                await printMessageWithMenu("⬅️ Back to the first page")

            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.")
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.")
    
    elif selectedMenu == menuFlags.SELECT_REGION_P3:
        match update.message.text:

            case "➡️ Next Page (4/4)":
                selectedMenu = menuFlags.SELECT_REGION_P4
                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 4:")
            
            case "⬅️ Back to 2° page":
                selectedMenu = menuFlags.SELECT_REGION_P2
                await printMessageWithMenu("⬅️ Back to the second page")
            
            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.")
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.")
    
    elif selectedMenu == menuFlags.SELECT_REGION_P4:
        match update.message.text:

            case "⬅️ Back to 3° page":
                selectedMenu = menuFlags.SELECT_REGION_P3
                await printMessageWithMenu("⬅️ Back to the third page")

            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.")
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.")

    elif selectedMenu == menuFlags.AUTOMATED_RUN:
        match update.message.text:

            case "⬅️ Back":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu")

            case "🕓 Set time":
                selectedMenu = menuFlags.SET_TIME
                await printMessageWithMenu(f"ℹ️ The time for the automatic execution is set to {settings.telegramAutoRunTime.strftime("%H:%M")} UTC.\nTo set a new one use the format HH:MM.")

            case "✅ Feature is enable" | "❌ Feature is disable":
                if settings.telegramAutoRun is True:
                    settings.telegramAutoRun = False

                    removeJob = None
                    for job in app.job_queue.scheduler.get_jobs():
                        if job.name == "automatedRun":
                            removeJob = job
                            break
                    
                    if removeJob is not None:
                        try:
                            app.job_queue.scheduler.remove_job(removeJob.id)
                            await printMessageWithMenu("ℹ️ Automated run feature is disable")
                        except JobLookupError:
                            await printMessageWithMenu("⚠️ Failed to remove the automated run job.")
                    else:
                        await printMessageWithMenu("⚠️ Automated run job not found. It might already be disabled.")

                else:
                    settings.telegramAutoRun = True
                    app.job_queue.run_daily(runCommand, time = settings.telegramAutoRunTime, name = "automatedRun")

                    await printMessageWithMenu("ℹ️ Automated run feature is enable")

            case _:
                await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.")
    
    elif selectedMenu == menuFlags.SET_TIME:
        match update.message.text:

            case "⬅️ Back":
                selectedMenu = menuFlags.AUTOMATED_RUN
                await printMessageWithMenu("⬅️ Back to the automated run menu")
            
            case _:
                try:
                    settings.telegramAutoRunTime = datetime.datetime.strptime(update.message.text, "%H:%M")
                    selectedMenu = menuFlags.AUTOMATED_RUN

                    await printMessageWithMenu("ℹ️ The time is set correctly")
                except ValueError:
                    await printMessageWithMenu(f"⚠️ '{update.message.text}' it is not a correct time formatted HH:MM")
                    return
                
                if settings.telegramAutoRun == True:
                    removeJob = None
                    for job in app.job_queue.scheduler.get_jobs():
                        if job.name == "automatedRun":
                            removeJob = job
                            break
                    
                    if removeJob is not None:
                        try:
                            app.job_queue.scheduler.remove_job(removeJob.id)
                        except JobLookupError:
                            await printMessageWithMenu("⚠️ Failed to remove the automated run job.")
                    else:
                        await printMessageWithMenu("⚠️ Automated run job not found. It might already be disabled.")
                    
                    app.job_queue.run_daily(runCommand, time = settings.telegramAutoRunTime, name = "automatedRun")
                    
                    await printMessageWithMenu("ℹ️ The autorun has been restarted successfully")

    else:
        await printMessageWithMenu("⚠️ Command not recognized.")

    return

def main() -> None:
    global bot
    global app

    if settings.vesusRegionsToQuery == [] or settings.vesusRegionsToQuery == [""]:
        for region in REGIONS.keys():
            settings.vesusRegionsToQuery.append(region)

    loadChatID()

    if settings.telegramAPIKey == "":
        print("Error: Telegram API key not set")
        exit(-1)
    
    
    bot = Bot(token=settings.telegramAPIKey)
    app = ApplicationBuilder().token(settings.telegramAPIKey).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    
    if settings.telegramAutoRun is True:
        app.job_queue.run_daily(runCommand, time = settings.telegramAutoRunTime, name = "automatedRun")
    
    print("Telegram bot started.")
        
    try:
        app.run_polling()
    except KeyboardInterrupt:
        # BUG:  This doesn't print if you press ^C once, but it does if you press it twice. WTF
        # TODO: Try to make this print always (if I have time to do it)
        print("Shutting down the bot...", flush=True)
    finally:
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.run_until_complete(shutdown())
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            print("Bot has been stopped.", flush=True)

    return