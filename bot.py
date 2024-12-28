import asyncio
import logging
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db import add_training, get_training_by_date, init_db
import os


TOKEN_FILE = os.getenv("BOT_TOKEN_FILE", "/run/secrets/bot_token")
try:
    with open(TOKEN_FILE, 'r') as file:
        BOT_TOKEN = file.read().strip()
except Exception as err:
    raise RuntimeError(f"Failed to read the token file: {err}")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided. Check your Docker secrets configuration.")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Welcome! I am your training bot. Use /help to see available commands.")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(
        "/get_recommendations - Get train recommendations\n"
        "/get_training - Get training by date\n"
        "/info - Description of train characteristics"
    )
    
@dp.message_handler(commands=['info'])
async def info_command(message: types.Message):
    description = (
        "📝 *Train characteristics:*\n"
        "▫️ *Type*: Light | Marathon | Tempo | Interval | Repeated\n"
        "▫️ *Duration* - training time\n"
        "▫️ *Time in Heart Rate Zones (per max heart rate)*: 65–79%, 80–90%, 88–92%, 98–100%, 100%\n"
        "▫️ *Cadence* - number of steps per minute\n"
        "▫️ *Distance* - run length\n"
        "▫️ *Date* - training date in the format YYYY-MM-DD\n"
    )
    await message.reply(description, parse_mode="Markdown")

@dp.message_handler(commands=['get_recommendations'])
async def add_training_command(message: types.Message):
    description = (
        "*Please enter your training data in the following format:*\n"
        "<Training type>\n"
        "<Duration (min)>\n"
        "<Time in heart rate zones (min)>\n"
        "<Cadence>\n"
        "<Distance (km)>\n"
        "<Date (YYYY-MM-DD)>\n"
        "`For more details use /info`\n"
        "----------------------------\n"
        "🛠 *Example*:\nTempo\n60\n15, 0, 45, 0, 0\n180\n12\n2024-12-20\n"
    )
    await message.reply(description, parse_mode="Markdown")

@dp.message_handler(lambda message: '\n' in message.text and ',' in message.text)
async def handle_message(message: types.Message):
    try:
        user_id = message.from_user.id
        training_data = message.text.split('\n')
        training_type = training_data[0]
        duration = float(training_data[1])
        heart_rate_zones = training_data[2]
        cadence = int(training_data[3])
        distance = float(training_data[4])
        date = training_data[5]

        heart_rate_zones_list = list(map(float, heart_rate_zones.split(', ')))
        recommendations = await give_recommendations(message, training_type, duration, heart_rate_zones_list, cadence, distance)
        await add_training(user_id, training_type, duration, heart_rate_zones, cadence, distance, date, recommendations)
        
    except Exception as err:
    	logging.error(f"Error saving training data: {err}")
    	await message.reply("Invalid format or error saving data. Please try again.")


async def give_recommendations(message, training_type, duration, heart_rate_zones, cadence, distance):
    recommendations = ""
    recommendations += "---------- *Pace* ----------\n"
    if training_type == "Light":
         if heart_rate_zones[0] >= 60 and heart_rate_zones[1] <= 3 and heart_rate_zones[2] == heart_rate_zones[3] == heart_rate_zones[4] == 0:
             recommendations += "Good pace\n"
         else:
             if heart_rate_zones[0] < 60:
                 recommendations += "Ran a little at easy pace\n"
             else:
                 recommendations += "Ran enough at easy pace\n"
             if heart_rate_zones[1] > 3 or heart_rate_zones[2] > 0 or heart_rate_zones[3] > 0 or heart_rate_zones[4] > 0:
                 recommendations += "A lot of acceleration\n"
             
    elif training_type == "Marathon":
        if heart_rate_zones[1] >= 60 and heart_rate_zones[2] <= 3 and heart_rate_zones[3] == heart_rate_zones[4] == 0:
             recommendations += "Good pace\n"
        else:
            if heart_rate_zones[1] < 60:
                recommendations += "Ran a little at marathon pace\n"
            else:
                recommendations += "Ran enough at marathon pace\n"
            if heart_rate_zones[2] > 3 or heart_rate_zones[3] > 0 or heart_rate_zones[4] > 0:
                recommendations += "A lot of acceleration\n"
    
    elif training_type == "Tempo":
        if heart_rate_zones[2] >= 60 and heart_rate_zones[3] <= 0.5 and heart_rate_zones[4] == 0:
            recommendations += "Good pace\n"
        else:
            if heart_rate_zones[2] < 60:
                recommendations += "Ran a little at tempo pace\n"
            else:
                recommendations += "Ran enough at tempo pace\n"
            if heart_rate_zones[3] > 0.5 or heart_rate_zones[4] > 0:
                recommendations += "A lot of acceleration\n"

    elif training_type == "Interval":
        if 9 <= heart_rate_zones[3] <= 15 and heart_rate_zones[4] <= 1.5:
            recommendations += "Good pace\n"
        else:
            if heart_rate_zones[3] < 9:
                recommendations += "Ran a little at interval pace\n"
            elif heart_rate_zones[3] > 15:
            	recommendations += "Ran too much at interval pace\n"
            else:
                recommendations += "Ran enough at interval pace\n"
            if heart_rate_zones[4] > 1.5:
                recommendations += "A lot of acceleration\n"
    
    elif training_type == "Repeated":
        if 5 <= heart_rate_zones[4] <= 9:
            recommendations += "Good pace\n"
        else:
            if heart_rate_zones[4] < 5:
                recommendations += "Ran a little at repeated pace\n"
            elif heart_rate_zones[3] > 9:
            	recommendations += "Ran too much at repeated pace\n"
            else:
                recommendations += "Ran enough at repeated pace\n"
             
                
    recommendations += "---------- *Duration* ----------\n"
    if 40 <= duration <= 90:
        recommendations += "Good running duration\n"
    elif duration < 40:
        recommendations += "Didn't train much\n"
    elif duration > 90:
        recommendations += "Too much load\n"
        
    recommendations += "---------- *Cadence* ----------\n"
    if 175 <= cadence <= 185:
        recommendations += "Good cadence"
    elif cadence < 175:
        recommendations += "Increase the cadence"
    elif cadence > 185:
        recommendations += "Decrease the cadence"
        
    await message.reply(recommendations, parse_mode="Markdown")
    return recommendations


@dp.message_handler(commands=['get_training'])
async def get_training_command(message: types.Message):
    await message.reply("Please enter the date (YYYY-MM-DD) to get your training data.")

@dp.message_handler(lambda message: '-' in message.text)
async def handle_date_request(message: types.Message):
    try:
        user_id = message.from_user.id
        date = message.text
        trainings = await get_training_by_date(user_id, date)

        if trainings:
            response = "\n▫️▫️▫️▫️▫️▫️▫️▫️▫️\n".join(
                [f"*Type:* {t[2]}\n*Duration:* {t[3]} mins\n*HR Zones:* {t[4]}\n*Cadence:* {t[5]}\n*Distance:* {t[6]} km\n*Recommendations:*\n {t[8]}"
                 for t in trainings]
            )
            await message.reply(response, parse_mode="Markdown")
        else:
            await message.reply("No training data found for this date.")
    except Exception as err:
        logging.error(f"Error fetching training data: {err}")
        await message.reply("Invalid date or error fetching data. Please try again.")

@dp.message_handler()
async def handle_unknown_message(message: types.Message):
    await message.reply("Invalid input. Please use /help to see the available commands.")

async def on_startup(dispatcher):
    await init_db()

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)







