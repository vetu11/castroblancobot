# coding=utf-8

import logging
import constantes
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, BaseFilter, MessageHandler
from GameManager import GameManager
from credenciales import BOT_TOKEN
from lang.lang import Lang

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class ForwardedFromSelfBot(BaseFilter):
    """ Filtro customizado para encotrar mensajes reenviados que pertenecen al bot """

    def filter(self, message):

        if message.forward_from and message.forward_from.id == constantes.extra.bot_id:
            return True
        return False


forwarded_from_self_bot = ForwardedFromSelfBot()


def stop_bot(updater):
    print "Apagando bot..."
    updater.stop()
    print "Bot apagado"


def ping(bot, update):
    update.message.reply_text("Pong!")


def start(bot, update):
    update.message.reply_text(Lang.get_text("start"), quote=False)


def callback_query_unexpected(bot, update):
    print "Se ha recibido un callback_query no esperado: %s" % update.callback_query.data
    update.callback_query.answer("Error: paquete de llamada no esperado", show_alert=True)


def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    a = dispatcher.add_handler

    constantes.extra.bot_id = updater.bot.id
    a(CommandHandler('start', start, filters=Filters.private))
    a(CommandHandler('ping', ping))
    a(CommandHandler('newgame', GameManager.new_game, pass_user_data=True, pass_chat_data=True, filters=Filters.group))
    a(CallbackQueryHandler(GameManager.join_game,
                           pattern=r"(join_game|join_game_start_bot)$",
                           pass_chat_data=True,
                           pass_user_data=True))
    a(CommandHandler('startgame', GameManager.force_start, pass_user_data=True,
                     pass_chat_data=True,
                     filters=Filters.group,
                     pass_job_queue=True))
    a(CallbackQueryHandler(GameManager.lobo_mata,
                           pattern=r"lobo_mata_a\*\d+\*partida_en\*-*\d+",
                           pass_user_data=True))
    a(CallbackQueryHandler(GameManager.vidente_observa,
                           pattern=r"vidente_observa_a\*\d+\*partida_en\*-*\d+"))
    a(CallbackQueryHandler(GameManager.ciudadano_vota,
                           pattern=r"ciudadano_vota_a\*\d+\*partida_en\*-*\d+",
                           pass_user_data=True))
    a(MessageHandler(filters=Filters.group and forwarded_from_self_bot,
                     callback=GameManager.mensaje_no_permitido,
                     pass_user_data=True))
    a(CallbackQueryHandler(callback_query_unexpected))
    a(CommandHandler('time', GameManager.time))

    updater.start_polling(clean=True)

    # CONSOLA
    while True:
        inp = raw_input()
        if inp:
            input_c = inp.split()[0]
            args = inp.split()[1:]
            strig = ""

            for e in args:
                strig = strig + " " + e

            if input_c == "stop":
                stop_bot(updater)
                break

            else:
                print "Comando desconocido"


if __name__ == '__main__':
    main()
