import traceback
import datetime
from typing import Optional
from enum import IntFlag

from telegram import Bot, error, Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from src.logNSet import settings, logger, engineFlags, REGIONS
from src.engine import engine


class menuFlags(IntFlag):
    MAIN_MENU = 0
    QUERY_NAME = 1
    SELECT_ENGINE = 2
    SELECT_REGION_P1 = 3
    SELECT_REGION_P2 = 4
    SELECT_REGION_P3 = 5
    SELECT_REGION_P4 = 6
selectedMenu: menuFlags = menuFlags.MAIN_MENU

bot = None
savedChatIDs = []
MAX_LENGTH = 4000

class logTG(logger):

    @classmethod
    async def error(cls, msg: str, shouldExit: bool = False, timestamp: Optional[str] = None, stacktrace = None) -> None:
        
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

                print(f"Failed to send error message to chat ID {chatID}: {e}\nSee errorLogs file to see more informations")
                with open("errorLogs.txt", "a", encoding="utf-8") as logFile:
                    logFile.write(f"Failed to send error message to chat ID {chatID}: {e}\nSTACKTRACE:\n{errorDetails}\n")
        
        if stacktrace is not None:
            msg += f"\nSTACKTRACE:\n{stacktrace}"

        await super().error(msg, shouldExit = shouldExit, timestamp = timestamp)
        return


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

async def printMessageWithMenu(message: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    match selectedMenu:
        
        case menuFlags.MAIN_MENU:
            msgBlocks = splitMessage(message)

            if settings.selectedEngine & engineFlags.VESUS:
                for msg in msgBlocks:
                    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([["👤 Query", "⚙️ Engine", "🗺️ Select Regions"], ["▶️ Run"]], resize_keyboard=True), parse_mode="markdown")
            else:
                for msg in msgBlocks:
                    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([["👤 Query", "⚙️ Engine"], ["▶️ Run"]], resize_keyboard=True), parse_mode="markdown")

        case menuFlags.QUERY_NAME:
            await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([["⬅️ Back"]], resize_keyboard=True))
        
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
            
            await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

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
            
            await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([buttonsFirstRow, buttonsSecondRow, ["⬅️ Back (Main Menu)", "➡️ Next Page (2/4)"]], resize_keyboard=True))

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
            
            await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([buttonsFirstRow, buttonsSecondRow, ["⬅️ Back to 1° page", "➡️ Next Page (3/4)"]], resize_keyboard=True))

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
            
            await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([buttonsFirstRow, buttonsSecondRow, ["⬅️ Back to 2° page", "➡️ Next Page (4/4)"]], resize_keyboard=True))

        case menuFlags.SELECT_REGION_P4:
            buttonsFirstRow = []
            for region in list(REGIONS.keys())[18:]:
                if region in settings.vesusRegionsToQuery:
                    buttonsFirstRow.append(f"✅ {region}")
                else:
                    buttonsFirstRow.append(f"❌ {region}")
            
            await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([buttonsFirstRow, ["⬅️ Back to 3° page"]], resize_keyboard=True))

        case _:
            await update.message.reply_text("Command not recognized.", resize_keyboard=True)
            return

    return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global selectedMenu
    selectedMenu = menuFlags.MAIN_MENU

    saveChatID(str(update.message.chat_id))

    await printMessageWithMenu("Telegram bot interface for [TNcontrol](https://github.com/AndreaStefanh/TNcontrol)", update, context)
    return

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

                await printMessageWithMenu(output, update, context)
            
            case "⚙️ Engine":
                selectedMenu = menuFlags.SELECT_ENGINE

                await printMessageWithMenu("ℹ️ Current engine settings:", update, context)

            case "▶️ Run":
                if settings.queryName == "":
                    await printMessageWithMenu("⚠️ Please enter a query name before running the bot.", update, context)
                    return
                
                if settings.selectedEngine == engineFlags.NONE:
                    await printMessageWithMenu("⚠️ Please select at least one engine before running the bot.", update, context)
                    return
                
                await update.message.reply_text("⏳ Loading...")

                try:
                    result = await engine.start(logTG())
                except Exception as e:
                    errorDetails = traceback.format_exc()
                    await logTG.error(f"Error while running the bot: {e}\nSee errorLogs file to see more informations.", stacktrace = errorDetails)
                    return
                
                msg = ""

                if settings.selectedEngine & engineFlags.VESUS:
                    msg = f"Using the keyword: '{escapeMarkdown(settings.queryName)}' for seeing the Vesus pre-registrations, I found the following tournaments:\n\n"
                    vesusResult = result[0]

                    for tournament in vesusResult:
                        for shortKey in tournament:
                            msg += f"🔹 *Tournament Name:* {escapeMarkdown(tournament[shortKey]['tornument'])}\n"
                            msg += f"📍 *Place:* {escapeMarkdown(tournament[shortKey]['location'])}\n"
                            msg += f"📅 *End of registration:* {escapeMarkdown(tournament[shortKey]['endRegistration'])}\n"
                            msg += f"🎯 *Start of tournament:* {escapeMarkdown(tournament[shortKey]['startTornument'])}\n"
                            msg += f"🔗 [Tournament Link](https://www.vesus.org/tournament/{shortKey})\n"
                            msg += f"👥 *Who There:*\n"
                            for names in tournament[shortKey]["name"]:
                                msg += f"  - {escapeMarkdown(names)}\n"
                            msg += "\n"
                
                if settings.selectedEngine & engineFlags.CIGU18:
                    if settings.selectedEngine & engineFlags.VESUS:
                        GIGResult = result[1]
                    else:
                        GIGResult = result[0]
                    
                    msg += f"Using the keyword: '{escapeMarkdown(settings.queryName)}' in the qualified CIGU18 FSI database, I found:\n"

                    for quialified in GIGResult:
                        msg += "\n"
                        msg += f"👤 *Name:* {escapeMarkdown(quialified[1])}\n"

                        for k, v in REGIONS.items():
                            if v == quialified[5]:
                                msg += f"🗺️ *Region:* {escapeMarkdown(k)}\n"
                                break
                        #msg += f" 🗺️ *Region:* {escapeMarkdown(quialified[5])}\n"

                        msg += f"📍 *Province:* {escapeMarkdown(quialified[4])}\n"
                        msg += f"🎂 *Birthdate:* {escapeMarkdown(quialified[2])} (YYYY-MM-DD)\n"
                        msg += f"⚧️ *Sex:* {escapeMarkdown(quialified[6])}\n"
                        msg += f"🇮🇹 *FSI ID:* {escapeMarkdown(quialified[0])}\n"
                        msg += f"🏢 *Club ID:* {escapeMarkdown(quialified[3])}\n"
                
                await printMessageWithMenu(msg, update, context)

            case "🗺️ Select Regions":
                selectedMenu = menuFlags.SELECT_REGION_P1

                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 1:", update, context)
            
            case _:
                await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)

    elif selectedMenu == menuFlags.QUERY_NAME:
        match update.message.text:

            case "⬅️ Back":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu", update, context)

            case _:
                settings.queryName = update.message.text
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu(f"ℹ️ Query name set to '{settings.queryName}'.", update, context)
    
    elif selectedMenu == menuFlags.SELECT_ENGINE:
        match update.message.text:

            case "✅ Vesus" | "❌ Vesus":
                settings.selectedEngine ^= engineFlags.VESUS
                await printMessageWithMenu("ℹ️ Vesus engine toggled.", update, context)

            case "✅ CIGU18" | "❌ CIGU18":
                settings.selectedEngine ^= engineFlags.CIGU18
                await printMessageWithMenu("ℹ️ CIGU18 engine toggled.", update, context)

            case "⬅️ Back":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu", update, context)

            case _:
                await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
    
    elif selectedMenu == menuFlags.SELECT_REGION_P1:
        match update.message.text:

            case "➡️ Next Page (2/4)":
                selectedMenu = menuFlags.SELECT_REGION_P2
                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 2:", update, context)

            case "⬅️ Back (Main Menu)":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu", update, context)
            
            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.", update, context)
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.", update, context)
        
    elif selectedMenu == menuFlags.SELECT_REGION_P2:
        match update.message.text:

            case "➡️ Next Page (3/4)":
                selectedMenu = menuFlags.SELECT_REGION_P3
                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 3:", update, context)

            case "⬅️ Back to 1° page":
                selectedMenu = menuFlags.SELECT_REGION_P1
                await printMessageWithMenu("⬅️ Back to the first page", update, context)

            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.", update, context)
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.", update, context)
    
    elif selectedMenu == menuFlags.SELECT_REGION_P3:
        match update.message.text:

            case "➡️ Next Page (4/4)":
                selectedMenu = menuFlags.SELECT_REGION_P4
                await printMessageWithMenu("ℹ️ Current italian regions to query for the vesus engine. Page 4:", update, context)
            
            case "⬅️ Back to 2° page":
                selectedMenu = menuFlags.SELECT_REGION_P2
                await printMessageWithMenu("⬅️ Back to the second page", update, context)
            
            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.", update, context)
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.", update, context)
    
    elif selectedMenu == menuFlags.SELECT_REGION_P4:
        match update.message.text:

            case "⬅️ Back to 3° page":
                selectedMenu = menuFlags.SELECT_REGION_P3
                await printMessageWithMenu("⬅️ Back to the third page", update, context)

            case _:
                msg = update.message.text
                region = ""

                if msg.startswith("✅ "):
                    region = msg.replace("✅ ", "").strip()
                elif msg.startswith("❌ "):
                    region = msg.replace("❌ ", "").strip()
                else:
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region not in REGIONS.keys():
                    await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
                    return

                if region in settings.vesusRegionsToQuery:
                    settings.vesusRegionsToQuery.remove(region)
                    await printMessageWithMenu(f"ℹ️ {region} region removed from the query.", update, context)
                else:
                    settings.vesusRegionsToQuery.append(region)
                    await printMessageWithMenu(f"ℹ️ {region} region added to the query.", update, context)

    else:
        await printMessageWithMenu("⚠️ Command not recognized.", update, context)

    return

def main() -> None:
    global bot

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

    print("Telegram bot started.")

    app.run_polling()
    return