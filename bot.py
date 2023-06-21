import os
import pandas as pd
import telebot
import json
from datetime import date
import schedule
from threading import Thread
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

SHEET_ID = '1GU9NAf7rjpigO52UbYtDkGeSLBfq2d_ofFysZTdlf9A'
SHEET_NAME = 'bot'

first_ack = False
second_ack = False

def remind():
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
        bot.send_message(chat_id=str(morning_tele_id), text='Reminder! It is your duty tomorrow morning. Please acknowledge!')
        bot.send_message(chat_id=str(night_tele_id), text='Reminder! It is your duty tomorrow night. Please acknowledge!')
        bot.send_message(-1001986573862, "Reminder sent!")
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = telebot.types.KeyboardButton('Noted! Thanks!')
        itembtn2 = telebot.types.KeyboardButton('I cannot make it!')
        markup.add(itembtn1, itembtn2)
        bot.send_message(str(morning_tele_id), "Please Acknowledge:", reply_markup=markup)
        bot.send_message(str(night_tele_id), "Please Acknowledge:", reply_markup=markup)
    except Exception as e:
        bot.send_message(-1001986573862, "Error! Please check the names in the Google Sheet. I may not have their Telegram IDs.")
        print(e)
        return


@bot.message_handler(regexp='Noted! Thanks!')
def acknowledge(message):
    if (first_ack == False):
        first_ack = True
    else:
        second_ack = True
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message,text = "Thank you for acknowledging!", reply_markup=markup)
    bot.send_message(-1001986573862, str(message.from_user.username) + " has acknowledged for duty.")


@bot.message_handler(regexp='I cannot make it!')
def alert(message):
    if (first_ack == False):
        first_ack = True
    else:
        second_ack = True
    markup = telebot.types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text = "Thank you for responding, the MeowHouse comm will arrange for a replacement!", reply_markup=markup)
    bot.send_message(-1001986573862, str(message.from_user.username) + " cannot make it for duty tomorrow! Please arrange for a replacement!")


@bot.message_handler(regexp= r'.*')
def record(message):
    chat_id = message.chat.id
    username = message.from_user.username
    
    data = {
        "chat_id": chat_id,
        "username": username
    }

    # Load existing data from chat_ids.json
    try:
        with open("chat_ids.json", "r") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    if not any(d['username'] == username for d in existing_data):
        # Append new data to the existing data
        existing_data.append(data)
    # Write the updated data to chat_ids.json
    with open("chat_ids.json", "w") as file:
        json.dump(existing_data, file)

    bot.reply_to(message, text= "Your Telegram ID has been recorded!")


def follow_up():
    if first_ack & second_ack:
        return 
    else:
        bot.send_message(-1001986573862, "Please check on tomorrow's duty! Someone has not responded!")


# Schedule the daily task to run every day at a specific time
schedule.every().day.at("18:00").do(remind)
schedule.every().day.at("19:00").do(follow_up)



def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Sleep for 60 seconds

def run_telegram_bot():
    bot.infinity_polling()

# Create and start a thread for running scheduled tasks
scheduled_tasks_thread = Thread(target=run_scheduled_tasks)
scheduled_tasks_thread.start()

# Run the Telegram bot in the main thread
run_telegram_bot()