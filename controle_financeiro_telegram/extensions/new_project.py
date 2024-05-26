from sqlalchemy import select
from telebot.handler_backends import StatesGroup, State

from controle_financeiro_telegram.database import Session
from controle_financeiro_telegram.models import Client, Project


class NewProjectStates(StatesGroup):
    client_name = State()
    total_value = State()
    entry_value = State()
    installment = State()


def init_bot(bot, start):
    @bot.callback_query_handler(func=lambda c: c.data == 'new_project')
    def new_project(callback_query):
        bot.send_message(
            callback_query.message.chat.id, 'Digite o nome do cliente'
        )
        bot.set_state(callback_query.message.chat.id, NewProjectStates.client_name, callback_query.message.chat.id)

    @bot.message_handler(state=NewProjectStates.client_name)
    def on_client_name(message):
        with bot.retrieve_data(message.chat.id, message.chat.id) as data:
            data['client_name'] = message.text
        bot.send_message(message.chat.id, 'Digite o valor total')
        bot.set_state(message.chat.id, NewProjectStates.total_value, message.chat.id)

    @bot.message_handler(state=NewProjectStates.total_value)
    def on_total_value(message):
        try:
            with bot.retrieve_data(message.chat.id, message.chat.id) as data:
                data['total_value'] = float(
                    message.text.replace('.', '').replace(',', '.')
                )
            bot.send_message(message.chat.id, 'Digite o valor de entrada')
            bot.set_state(message.chat.id, NewProjectStates.entry_value, message.chat.id)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.set_state(message.chat.id, NewProjectStates.total_value, message.chat.id)

    @bot.message_handler(state=NewProjectStates.entry_value)
    def on_entry_value(message):
        try:
            with bot.retrieve_data(message.chat.id, message.chat.id) as data:
                data['entry_value'] = float(
                    message.text.replace('.', '').replace(',', '.')
                )
                if data['entry_value'] > data['total_value']:
                    bot.send_message(
                        message.chat.id, 'Valor da entrada não pode ser maior que o valor total'
                    )
                    bot.set_state(message.chat.id, NewProjectStates.entry_value, message.chat.id)
                    return
            bot.send_message(
                message.chat.id,
                'Digite o números de parcelas (0 para a vista)',
            )
            bot.set_state(message.chat.id, NewProjectStates.installment, message.chat.id)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.set_state(message.chat.id, NewProjectStates.entry_value, message.chat.id)

    @bot.message_handler(state=NewProjectStates.installment)
    def on_installment(message):
        try:
            with Session() as session:
                with bot.retrieve_data(
                    message.chat.id, message.chat.id
                ) as data:
                    query = select(Client).where(
                        Client.nome == data['client_name']
                    )
                    client = session.scalars(query).first()
                    if client is None:
                        client = Client(
                            nome=data['client_name'],
                        )
                        session.add(client)
                        session.flush()
                    project = Project(
                        cliente=client,
                        valor_total=data['total_value'],
                        entrada=data['entry_value'],
                        parcelas=int(message.text),
                    )
                    session.add(project)
                    session.commit()
                bot.send_message(message.chat.id, 'Projeto Criado!')
                start(message)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.set_state(message.chat.id, NewProjectStates.entry_value, message.chat.id)
