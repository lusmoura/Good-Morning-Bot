import os
import cohere
from dotenv import load_dotenv

from telegram.ext import *
from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class TelegramBot:
    tones = ['Relaxed', 'Happy', 'Enthusiastic', 'Thoughtful', 'Inspirational', 'Romantic', 'Religious', 'Sad', 'Depressive', 'Angry']

    def __init__(self) -> None:
        load_dotenv()
    
    def start(self, update, context):
        text = 'Good Morning! Welcome to CohereGoodMorningBot, here you\'ll get the best good morning messages generated by our models according to your mood.'
        context.bot.send_message(chat_id=update.message.chat_id, text=text)
    
    def help(self, update, context):
        commands = '''Here\'s what I can do: 
        /start - Start.
        /get - Get new message.
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

    def query_handler(self, update, context):
        query = update.callback_query
        query.answer()
        tone = query.data
        query.edit_message_text(text=f"Selected option: {tone}")
        text = self.get_text(tone)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


    def unknown(self, update, context):
        text = "Sorry, I didn\'t get it =(\n Try /help for more info."
        context.bot.send_message(chat_id=update.message.chat_id, text=text)

    def run(self) -> None:
        self.co = cohere.Client(os.getenv('COHERE_API_KEY'))
        updater = Updater(token=os.getenv('TELEGRAM_API_KEY'), use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        dispatcher.add_handler(help_handler)

        get_handler = CommandHandler('get', self.get)
        dispatcher.add_handler(get_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher.add_handler(unknown_handler)

        callback_handler = CallbackQueryHandler(self.query_handler)
        dispatcher.add_handler(callback_handler)

        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
