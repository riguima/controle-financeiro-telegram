from telebot.util import quick_markup
from sqlalchemy import select

from controle_financeiro_telegram.models import Receipt, Project
from controle_financeiro_telegram.database import Session


def init_bot(bot, start):
    @bot.callback_query_handler(func=lambda c: c.data == 'register_receipt')
    def register_receipt(callback_query):
        reply_markup = {}
        with Session() as session:
            for project in session.scalars(select(Project)).all():
                reply_markup[f'{project.cliente.nome} - R$ {project.valor_total:.2f}'.replace('.', ',')] = {
                    'callback_data': f'choose_project:{project.id}'
                }
            reply_markup['Voltar'] = {'callback_data': 'return_to_main_menu'}
        bot.send_message(callback_query.message.chat.id, 'Selecione o projeto', reply_markup=quick_markup(reply_markup, row_width=1))

    @bot.callback_query_handler(func=lambda c: 'choose_project:' in c.data)
    def choose_project(callback_query):
        project_id = int(callback_query.data.split(':')[-1])
        bot.send_message(callback_query.message.chat.id, 'Digite o valor')
        bot.register_next_step_handler(callback_query.message, lambda m: on_value(m, project_id))
    
    def on_value(message, project_id):
        try:
            with Session() as session:
                project = session.get(Project, project_id)
                receipt = Receipt(
                    projeto=project,
                    valor=float(message.text.replace('.', '').replace(',', '.'))
                )
                session.add(receipt)
                session.commit()
                bot.send_message(message.chat.id, 'Recebimento Adicionado!')
                start(message)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.register_next_step_handler(message, lambda m: on_value(m, project_id))
