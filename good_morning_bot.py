import os
import pytz
import random 
import cohere
import logging
import psycopg2

import pandas as pd

from datetime import time
from dotenv import load_dotenv
from pytz import timezone

from telegram.ext import *
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    tones = ['Relaxed', 'Happy', 'Enthusiastic', 'Thoughtful', 'Inspirational', 'Romantic', 'Religious', 'Sad', 'Depressive', 'Angry']

    def __init__(self) -> None:
        load_dotenv()
        self.PORT = int(os.environ.get('PORT', '8443'))
        self.DB_URL = os.environ.get('DB_URL')
        self.DB_PASSWORD = os.environ.get('DB_PASSWORD')
        query = 'CREATE TABLE IF NOT EXISTS users (id integer);'
        self.write_to_db(query)

    def start(self, update, context):
        logger.info('Start')
        text = 'Good Morning! Welcome to CohereGoodMorningBot, here you\'ll get the best good morning messages generated by our models according to your mood.'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

        user_name = update.message.from_user.name
        user_id = update.message.from_user.id
        self.db.set(user_name, user_id)
    
    def help(self, update, context):
        logger.info('Help')
        commands = '''Here\'s what I can do: 
        /start - Start.
        /get - Get new message.
        /subscribe - Receive daily good morning messages.
        /unsubscribe - Stop receiving daily messages.
        '''
        
        context.bot.send_message(chat_id=update.message.chat_id, text=commands)

    def pairwise(self, iterable):
        "s -> (s0, s1), (s2, s3), (s4, s5), ..."
        a = iter(iterable)
        return zip(a, a)

    def get_tone_buttons(self):
        buttons = []

        for tone1, tone2 in self.pairwise(self.tones):
            buttons.append([InlineKeyboardButton(text=tone1, callback_data=f'{tone1}'),
                        InlineKeyboardButton(text=tone2, callback_data=f'{tone2}')])
        
        markup = InlineKeyboardMarkup(buttons)
        return markup

    def get(self, update, context):
        logger.info('Get')
        buttons = self.get_tone_buttons()
        context.bot.send_message(chat_id=update.message.chat_id,
                                text='Which mood do you want for your message?',
                                reply_markup=buttons,
                                parse_mode='HTML'
                                )

    def get_text(self, tone):
        prediction = self.co.generate(
        model='large',
        prompt=f'''Tone: Romantic
        Message: Hello, sweetie. How are you? I really enjoyed our last night together by making a lot of fun. You are indeed amazing. I hope you have a wonderful day today!
        --
        Tone: Romantic
        Message: I really hope you had a good sleep. Please walk up now since my mornings are really incomplete without you. Good morning Jaan!
        --
        Tone: Romantic
        Message: Every morning for me is an opportunity to love, respect, care for you, and make you feel so amazing all day long. Good morning my sweetheart!
        --
        Tone: Thoughtful
        Message: If you have the willpower to win your snooze button, no one can stop you from turning your dreams into reality. Have a great day! Happy Good Morning!
        --
        Tone: Inspirational
        Message: Every morning gives you a new opportunity. You have to just go out grab with full zeal. Keep smiling at the start of this new day. Have a blessed and spectacular good morning.
        --
        Tone: Inspirational
        Message: Never believe in taking motivation and inspiration. Always believe in yourself and make your own way to achieve your goal. Good morning!
        --
        Tone: Religous
        Message: I pray to God this beautiful morning he accepts all your prayers in no time. Have an outstanding day with lots of love!
        --
        Tone: Religious
        Message: Have a blessed morning to you, dear! May you receive strength and power to put up with troubles. May life be joyful and blessed. Good Morning!
        --
        Tone: Sad 
        Message: I have been so sad since morning because I am not with you. I have missed you so much. Good Morning!
        --
        Tone: Depressive
        Message: You are worth the life of a beautiful morning. I miss you so much. Have a sad morning, my love!
        --
        Tone: {tone}
        Message: ''',
        max_tokens=100,
        temperature=0.8,
        k=0,
        p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop_sequences=["--"],
        return_likelihoods='NONE')

        text = prediction.generations[0].text
        text = text.replace('--', '').strip()
        return text

    def write_to_db(self, query):
        conn = psycopg2.connect(self.DB_URL, sslmode='require', password=self.DB_PASSWORD)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()

    def read_from_db(self, query):
        conn = psycopg2.connect(self.DB_URL, sslmode='require', password=self.DB_PASSWORD)
        user_data = pd.read_sql(query, conn)
        return user_data.to_dict('records')[0]

    def subscribe(self, update, context):
        chat_id = update.message.chat_id
        query = f"""INSERT INTO users(id) VALUES ({chat_id}) ON CONFLICT DO NOTHING;"""
        self.write_to_db(query)
        text = 'Done! You\'ll receive a daily good morning message!'
        context.bot.send_message(chat_id=chat_id, text=text)
    
    def unsubscribe(self, update, context):
        chat_id = update.message.chat_id
        query = f"""DELETE FROM users WHERE id= {chat_id}"""
        self.write_to_db(query)
        text = 'Okay! No more good morning messages for you =('
        context.bot.send_message(chat_id=chat_id, text=text)

    def send_random_message(self, context):
        logger.info('Sending scheduled message')
        users = self.read_from_db('''SELECT * FROM users''')
        
        tone = random.choice(self.tones)
        text = self.get_text(tone)
        
        for id in users:
            context.bot.send_message(chat_id=id, text=f'Here\'s your scheduled message =D\nToday you\'ll get a {tone} message')
            context.bot.send_message(chat_id=id, text=text)

    def query_handler(self, update, context):
        query = update.callback_query
        query.answer()
        tone = query.data
        query.edit_message_text(text=f"Selected option: {tone}")
        text = self.get_text(tone)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def unknown(self, update, context):
        logger.info('Unknown')
        text = "Sorry, I didn\'t get it =(\n Try /help for more info."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

    def error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def run(self) -> None:
        logger.info('Starting')
        self.co = cohere.Client(os.environ.get('COHERE_API_KEY'))
        updater = Updater(token=os.environ.get('TELEGRAM_API_KEY'), use_context=True)
        dispatcher = updater.dispatcher
        job_queue = updater.job_queue

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        dispatcher.add_handler(help_handler)

        get_handler = CommandHandler('get', self.get)
        dispatcher.add_handler(get_handler)

        subscribe_handler = CommandHandler('subscribe', self.subscribe)
        dispatcher.add_handler(subscribe_handler)

        unsubscribe_handler = CommandHandler('unsubscribe', self.unsubscribe)
        dispatcher.add_handler(unsubscribe_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher.add_handler(unknown_handler)

        callback_handler = CallbackQueryHandler(self.query_handler)
        dispatcher.add_handler(callback_handler)

        dispatcher.add_error_handler(self.error)

        job_queue.run_daily(self.send_random_message, time=time(hour=16, minute=24, second=00, tzinfo=timezone('America/Sao_Paulo')))
    
        updater.start_webhook(
            listen="0.0.0.0",
            port=self.PORT,
            url_path=os.environ.get('TELEGRAM_API_KEY'),
            webhook_url=os.environ.get('APP_NAME') + os.environ.get('TELEGRAM_API_KEY')
        )
        
        # updater.start_polling(timeout=6000)
        updater.idle()

if __name__ == '__main__':
    bot = TelegramBot()
    try:
        bot.run()
    except Exception as e:
        logging.info(e.args)