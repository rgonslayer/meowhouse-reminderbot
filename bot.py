import os
import pandas as pd
import telebot
import json
from datetime import date

BOT_TOKEN = os.environ.get('BOT_TOKEN')
user_id = '@dylchew'
chat_id = ''
bot = telebot.TeleBot(BOT_TOKEN)

SHEET_ID = '1GU9NAf7rjpigO52UbYtDkGeSLBfq2d_ofFysZTdlf9A'
SHEET_NAME = 'bot'




@bot.message_handler(commands = ['remind'])
def remind(message):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)

    today = pd.to_datetime('today').normalize()  # Get today's date without time
    tomorrow = today + pd.DateOffset(days=1)  # Get tomorrow's date without time
    with open('./chat_ids.json', 'r') as json_file:
        data = json.load(json_file)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    morning = df.loc[tomorrow, 'Morning']
    night= df.loc[tomorrow, 'Night']
    print(morning)
    print(night)

    # Reset the index of the DataFrame
    df.reset_index(inplace=True)
    try:
        morning_tele_id = [x for x in data if x["name"] == morning][0]["chat_id"]
        night_tele_id = [x for x in data if x["name"] == night][0]["chat_id"]
        bot.send_message(chat_id=morning_tele_id, text='Reminder! It is your duty tomorrow morning. Please acknowledge!')
        bot.send_message(chat_id=night_tele_id, text='Reminder! It is your duty tomorrow night. Please acknowledge!')
        bot.reply_to(message, "Reminder sent!")
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = telebot.types.KeyboardButton('Noted! Thanks!')
        itembtn2 = telebot.types.KeyboardButton('I cannot make it!')
        markup.add(itembtn1, itembtn2)
        bot.send_message(morning_tele_id, "Please Acknowledge:", reply_markup=markup)
        bot.send_message(night_tele_id, "Please Acknowledge:", reply_markup=markup)
    except:
        bot.reply_to(message, "Error! Please check the names in the Google Sheet. I may not have their Telegram IDs.")
        return
@bot.message_handler(regexp='Noted! Thanks!')
def acknowledge(message):
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message,text = "Thank you for acknowledging!", reply_markup=markup)
    bot.send_message(-1001986573862, str(message.from_user.username) + " has acknowledged for duty.")


@bot.message_handler(regexp='I cannot make it!')
def alert(message):
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text = "Thank you for responding, the MeowHouse comm will arrange for a replacement!", reply_markup=markup)
    bot.send_message(-1001986573862, str(message.from_user.username) + " cannot make it for duty tomorrow! Please arrange for a replacement!")

bot.infinity_polling()