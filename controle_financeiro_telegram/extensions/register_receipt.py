from sqlalchemy import select
from telebot.util import quick_markup

from controle_financeiro_telegram.database import Session
from controle_financeiro_telegram.models import Project, Receipt


def init_bot(bot, start):
    @bot.callback_query_handler(func=lambda c: c.data == 'register_receipt')
    def register_receipt(callback_query):
        reply_markup = {}
        with Session() as session:
            for project in session.scalars(select(Project)).all():
                remaining_value = project.valor_total - sum([r.valor for r in project.recebimentos])
                reply_markup[
                    f'{project.cliente.nome} - Total: R$ {project.valor_total:.2f} - Restante {remaining_value:.2f}'.replace(
                        '.', ','
                    )
                ] = {'callback_data': f'choose_project:{project.id}'}
            reply_markup['Voltar'] = {'callback_data': 'return_to_main_menu'}
        bot.send_message(
            callback_query.message.chat.id,
            'Selecione o projeto',
            reply_markup=quick_markup(reply_markup, row_width=1),
        )

    @bot.callback_query_handler(func=lambda c: 'choose_project:' in c.data)
    def choose_project(callback_query):
        project_id = int(callback_query.data.split(':')[-1])
        with Session() as session:
            project = session.get(Project, project_id)
            remaining_value = project.valor_total - sum([r.valor for r in project.recebimentos])
            bot.send_message(callback_query.message.chat.id, f'Digite o valor (Valor restante: R$ {remaining_value:.2f})'.replace('.', ','))
            bot.register_next_step_handler(
                callback_query.message, lambda m: on_value(m, project_id)
            )

    def on_value(message, project_id):
        try:
            with Session() as session:
                project = session.get(Project, project_id)
                remaining_value = project.valor_total - sum([r.valor for r in project.recebimentos])
                value = float(message.text.replace('.', '').replace(',', '.'))
                if value > remaining_value:
                    bot.send_message(message.chat.id, 'O valor digitado não pode ser maior que o valor restante')
                    bot.register_next_step_handler(
                        message, lambda m: on_value(m, project_id)
                    )
                    return
                receipt = Receipt(
                    projeto=project,
                    valor=value,
                )
                session.add(receipt)
                session.commit()
                bot.send_message(message.chat.id, 'Recebimento Adicionado!')
                start(message)
        except ValueError:
            bot.send_message(
                message.chat.id, 'Valor inválido, digite somente números'
            )
            bot.register_next_step_handler(
                message, lambda m: on_value(m, project_id)
            )
