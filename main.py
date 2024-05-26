from importlib import import_module

import telebot
from telebot.custom_filters import StateFilter
from telebot.storage import StateMemoryStorage
from telebot.util import quick_markup

from controle_financeiro_telegram.config import config

bot = telebot.TeleBot(config['BOT_TOKEN'], state_storage=StateMemoryStorage())


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Escolha uma opção',
        reply_markup=quick_markup(
            {
                'Novo Projeto': {'callback_data': 'new_project'},
                'Registrar Recebimento': {'callback_data': 'register_receipt'},
                'Resumo': {'callback_data': 'summary'},
            },
            row_width=1,
        ),
    )


def load_extensions():
    for extension in config['EXTENSIONS']:
        extension_module = import_module(extension)
        extension_module.init_bot(bot, start)


if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    load_extensions()
    bot.infinity_polling()
