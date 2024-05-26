from telebot.util import quick_markup
from controle_financeiro_telegram.database import Session
from sqlalchemy import select
from controle_financeiro_telegram.models import Project
import prettytable


def init_bot(bot, start):
    @bot.callback_query_handler(func=lambda c: c.data == 'summary')
    def summary(callback_query):
        table = prettytable.PrettyTable(['Cliente', 'Total', 'Restante', 'Último Recebimento'])
        table.align['Cliente'] = 'c'
        table.align['Total'] = 'c'
        table.align['Restante'] = 'c'
        table.align['Último Recebimento'] = 'c'
        table.align['Data de registro'] = 'c'
        with Session() as session:
            for project in session.scalars(select(Project)).all():
                remaining_value = project.valor_total - sum([r.valor for r in project.recebimentos])
                if remaining_value > 0:
                    sorted_receipts = sorted(project.recebimentos, key=lambda r: r.data)
                    try:
                        table.add_row([project.cliente.nome, f'R$ {project.valor_total:.2f}'.replace('.', ','), f'R$ {remaining_value:.2f}'.replace('.', ','), f'{sorted_receipts[-1].data:%d/%m/%Y}', f'{project.data}:%d/%m/%Y'])
                    except IndexError:
                        table.add_row([project.cliente.nome, f'R$ {project.valor_total:.2f}'.replace('.', ','), f'R$ {remaining_value:.2f}'.replace('.', ','), 'Sem recebimento', f'{project.data}:%d/%m/%Y'])
        bot.send_message(callback_query.message.chat.id, f'```{table}```', reply_markup=quick_markup({
            'Voltar': {'callback_data': 'return_to_main_menu'}
        }), parse_mode='MarkdownV2')
