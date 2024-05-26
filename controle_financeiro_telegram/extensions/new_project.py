from sqlalchemy import select

from controle_financeiro_telegram.database import Session
from controle_financeiro_telegram.models import Client, Project


def init_bot(bot, start):
    @bot.callback_query_handler(func=lambda c: c.data == 'new_project')
    def new_project(callback_query):
        bot.send_message(
            callback_query.message.chat.id, 'Digite o nome do cliente'
        )
        bot.register_next_step_handler(callback_query.message, on_client_name)

    def on_client_name(message):
        with bot.retrieve_data(message.chat.id, message.chat.id) as data:
            data['client_name'] = message.text
        bot.send_message(message.chat.id, 'Digite o valor total')
        bot.register_next_step_handler(message, on_total_value)

    def on_total_value(message):
        try:
            with bot.retrieve_data(message.chat.id, message.chat.id) as data:
                data['total_value'] = float(
                    message.text.replace('.', '').replace(',', '.')
                )
            bot.send_message(message.chat.id, 'Digite o valor de entrada')
            bot.register_next_step_handler(message, on_entry_value)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.register_next_step_handler(message, on_total_value)

    def on_entry_value(message):
        try:
            with bot.retrieve_data(message.chat.id, message.chat.id) as data:
                data['entry_value'] = float(
                    message.text.replace('.', '').replace(',', '.')
                )
            bot.send_message(
                message.chat.id,
                'Digite o números de parcelas (0 para a vista)',
            )
            bot.register_next_step_handler(message, on_installment)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.register_next_step_handler(message, on_entry_value)

    def on_installment(message):
        try:
            with Session() as session:
                with bot.retrieve_data(
                    message.chat.id, message.chat.id
                ) as data:
                    query = select(Client).where(
                        Client.name == data['client_name']
                    )
                    client = session.scalars(query).first()
                    if client is None:
                        client = Client(
                            nome=data['client_name'],
                        )
                        session.add(client)
                        session.flush()
                    project = Project(
                        client=client,
                        valor_total=data['total_value'],
                        entrada=data['entry_value'],
                        parcelas=int(message.text),
                    )
                    session.add(project)
                    session.commit()
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.register_next_step_handler(message, on_installment)
