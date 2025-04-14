# TODO: add support for selectedRegion
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
selectedMenu: menuFlags = menuFlags.MAIN_MENU

bot = None
savedChatIDs = []

class logTG(logger):

    @classmethod
    async def error(cls, msg: str, shouldExit: bool = False, timestamp: Optional[str] = None) -> None:
        
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         
        print(f"[{timestamp}] ERROR: {msg}")

        for chatID in savedChatIDs:
            try:
                await bot.send_message(chat_id=chatID, text=f"⚠️ [{timestamp}] ERROR: {msg}")
            except error.TelegramError as e:
                print(f"Failed to send error message to chat ID {chatID}: {e}")
                with open("errorLogs.txt", "a", encoding="utf-8") as logFile:
                    logFile.write(f"Failed to send error message to chat ID {chatID}: {e}\n")

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

async def printMessageWithMenu(message: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    match selectedMenu:
        
        case menuFlags.MAIN_MENU:
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
                
                result = await engine.start(logTG())
                msg = ""

                if settings.selectedEngine & engineFlags.VESUS:
                    msg = f"Using the keyword: '{settings.queryName}' for seeing the Vesus pre-registrations, I found the following tournaments:\n\n"
                    vesusResult = result[0]

                    for tournament in vesusResult:
                        for shortKey in tournament:
                            msg += f"🔹 *Tournament Name:* {tournament[shortKey]['tornument']}\n"
                            msg += f"📍 *Place:* {tournament[shortKey]['location']}\n"
                            msg += f"📅 *End of registration:* {tournament[shortKey]['endRegistration']}\n"
                            msg += f"🎯 *Start of tournament:* {tournament[shortKey]['startTornument']}\n"
                            msg += f"🔗 [Tournament Link](https://www.vesus.org/tournament/{shortKey})\n"
                            msg += f"👥 *Who There:*\n"
                            for names in tournament[shortKey]["name"]:
                                msg += f"  - {names}\n"
                            msg += "\n"
                
                if settings.selectedEngine & engineFlags.CIGU18:
                    if settings.selectedEngine & engineFlags.VESUS:
                        GIGResult = result[1]
                    else:
                        GIGResult = result[0]
                    
                    msg += f"Using the keyword: '{settings.queryName}' in the qualified CIGU18 FSI database, I found:\n"

                    for quialified in GIGResult:
                        msg += "\n"
                        msg += f"👤 *Name:* {quialified[1]}\n"

                        for k, v in REGIONS.items():
                            if v == quialified[5]:
                                msg += f" 🗺️ *Region:* {k}\n"
                                break
                        #msg += f" 🗺️ *Region:* {quialified[5]}\n"

                        msg += f" 📍 *Province:* {quialified[4]}\n"
                        msg += f" 🎂 *Birthdate:* {quialified[2]} (YYYY-MM-DD)\n"
                        msg += f" ⚧️ *Sex:* {quialified[6]}\n"
                        msg += f" 🇮🇹 *FSI ID:* {quialified[0]}\n"
                        msg += f" 🏢 *Club ID:* {quialified[3]}\n"
                
                await printMessageWithMenu(msg, update, context)
            
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
                settings.selectedEngine ^= settings.selectedEngine.VESUS
                await printMessageWithMenu("ℹ️ Vesus engine toggled.", update, context)

            case "✅ CIGU18" | "❌ CIGU18":
                settings.selectedEngine ^= settings.selectedEngine.CIGU18
                await printMessageWithMenu("ℹ️ CIGU18 engine toggled.", update, context)

            case "⬅️ Back":
                selectedMenu = menuFlags.MAIN_MENU
                await printMessageWithMenu("⬅️ Back to main menu", update, context)

            case _:
                await printMessageWithMenu(f"⚠️ Command not recognized '{update.message.text}'.", update, context)
    
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

    app.run_polling()
    return