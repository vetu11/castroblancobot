# coding=utf-8

import datetime
from partida import Partida
from usuario import conseguir_usuario
from lang.lang import Lang
from credenciales import DEBUGGING, BOT_TOKEN
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, Bot, ParseMode
from grupo import conseguir_chat

BOT_USERNAME = Bot(BOT_TOKEN).get_me().username


# TODO: eliminar este metodo y meterlo todo en GameManager._iniciar_noche_lobos
def noche_lobo(bot, job, jugador):
    """Lanza un mensaje a un lobo con sus opciones para matar."""

    text, potenciales_victimas = jugador.personaje.accion_nocturna(job.context["partida"])
    keyboard = []

    for potencial_victima in potenciales_victimas:
        keyboard.append([InlineKeyboardButton(text=potencial_victima.nombre_completo_simple,
                                              callback_data="lobo_mata_a*%s*partida_en*%s" %
                                                            (potencial_victima.id, job.context["chat"].id))])
        if DEBUGGING:
            print "Creado teclado para %s en partida %s" % (potencial_victima.id, job.context["chat"].id)

    bot.send_message(chat_id=jugador.id,
                     text=text,
                     reply_markup=InlineKeyboardMarkup(keyboard))


# DEPRECATED
def generar_texto_varios_muertos(muertos):

    txt = ""
    for jugador in muertos:
        if jugador is muertos[-1]:
            txt += "%s (%s)" % (jugador.nombre_completo, jugador.personaje.nombre)
        elif jugador is muertos[-2]:
            txt += "%s (%s) y " % (jugador.nombre_completo, jugador.personaje.nombre)
        else:
            txt += "%s (%s), " % (jugador.nombre_completo, jugador.personaje.nombre)
    return txt


class GameManager:

    def __init__(self): # todo: cargar partidas al inicio y guardarlas ALWAYS
        """Administrador de partidas"""

        self.partidas = {}
        self.jugadores = {}

    @staticmethod
    def conseguir_partida(update, chat_data, **kargs):

        return kargs.get("chat", conseguir_chat(update, chat_data)).partida

    def new_game(self, bot, update, user_data, chat_data):  # TODO comprobar si el usuario ya está en una partida

        if DEBUGGING and update.effective_user.id != 254234845: return

        usuario = conseguir_usuario(update, user_data, self.jugadores)
        chat = conseguir_chat(update, chat_data)

        if not chat.partida:

            nueva_partida = Partida(usuario)

            self.partidas[update.effective_chat.id] = nueva_partida

            chat.partida = nueva_partida

        keyboard = [[InlineKeyboardButton("Unirse a la partida", callback_data="join_game")]]

        update.message.reply_text(Lang.get_text_inserted("start_game_successful",
                                                         player_list=chat.partida.text_player_list()),
                                  reply_markup=InlineKeyboardMarkup(keyboard),
                                  quote=False,
                                  disable_web_page_preview=True,
                                  parse_mode=ParseMode.MARKDOWN)

    def join_game(self, bot, update, user_data, chat_data):

        try:
            bot.send_chat_action(update.effective_user.id, ChatAction.TYPING)
            bot_iniciado = True
        except Exception, e:
            print "Exception yas"
            bot_iniciado = False

        usuario = conseguir_usuario(update, user_data, self.jugadores)
        partida = self.conseguir_partida(update, chat_data)
        keyboard = [[InlineKeyboardButton("Unirse a la partida", callback_data="join_game")]]
        start_keyboard = [[InlineKeyboardButton("1️⃣ Iniciar el bot", url="t.me/%s?start=refered_start_game" % BOT_USERNAME)],
                          [InlineKeyboardButton("2️⃣ Unirse a la partida", callback_data="join_game_start_bot")]]

        if not partida:
            if DEBUGGING:
                print "not partida"
            update.callback_query.answer(Lang.get_text("no_game_error"), show_alert=True)
            update.callback_query.message.edit_text(Lang.get_text("no_game_error"))
            return

        if partida.partida_empezada:
            if DEBUGGING:
                print "too late"
            update.callback_query.answer(Lang.get_text("too_late"))

        if not bot_iniciado:
            if DEBUGGING:
                print "BOT NO INICIADO"
            update.callback_query.message.edit_text(Lang.get_text_inserted("start_game_successful_please_start_bot",
                                                                           player_list=partida.text_player_list()),
                                                    reply_markup=InlineKeyboardMarkup(start_keyboard),
                                                    parse_mode=ParseMode.MARKDOWN,
                                                    disable_web_page_preview=True)
            update.callback_query.answer(Lang.get_text("bot_not_started"), show_alert=True)
            return

        if usuario in partida.jugadores:
            update.callback_query.answer(Lang.get_text("already_in_the_game"),
                                         show_alert=True)
            return

        partida.jugadores.append(usuario)
        self.jugadores[usuario.id] = usuario

        if DEBUGGING:
            print "Función join_game, dicc de jugadores=%s" % self.jugadores

        if update.callback_query.data == "join_game":
            update.callback_query.answer(Lang.get_text("join_successful"))
            update.callback_query.message.edit_text(Lang.get_text_inserted("start_game_successful",
                                                                           player_list=partida.text_player_list()),
                                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                                    parse_mode=ParseMode.MARKDOWN,
                                                    disable_web_page_preview=True)
        else:
            update.callback_query.answer(Lang.get_text("join_successful"))
            update.callback_query.message.edit_text(Lang.get_text_inserted("start_game_successful_please_start_bot",
                                                                           player_list=partida.text_player_list()),
                                                    reply_markup=InlineKeyboardMarkup(start_keyboard),
                                                    parse_mode=ParseMode.MARKDOWN,
                                                    disable_web_page_preview=True)

    def force_start(self, bot, update, user_data, chat_data, job_queue):

        if DEBUGGING and update.effective_user.id != 254234845: return  # TODO: comprobar si hay una partida.

        now_temp = datetime.datetime.now().time()

        # Comprobamos si es la hora del día correcta en la que se puede iniciar la partida
        if not DEBUGGING and (now_temp < datetime.time(hour=19) or now_temp > datetime.time(hour=19, minute=50)):
            update.effective_message.reply_text(Lang.get_text(text="wrong_time_to_start"), quote=False)
            return

        chat = conseguir_chat(update, chat_data)
        partida = self.conseguir_partida(update, chat_data, chat=chat)

        # Comprobamos si hay al menos 8 jugadores
        if not DEBUGGING and len(partida.jugadores) < 7:
            update.effective_message.reply_text(Lang.get_text(text="not_enough_players"), quote=False)
            return

        # Inicializamos la partida
        partida.iniciar_partida(bot, grupo=chat)

        # Añadimos los jobs a job_queue para las distintas fases de la partida
        if DEBUGGING:
            job_queue.run_repeating(self._iniciar_noche,
                                    datetime.timedelta(minutes=16),
                                    datetime.timedelta(seconds=1),
                                    context={"chat": chat, "partida": partida})
            job_queue.run_repeating(self._iniciar_anuncios,
                                    datetime.timedelta(minutes=16),
                                    datetime.timedelta(minutes=4),
                                    context={"chat": chat, "partida": partida})
            job_queue.run_repeating(self._iniciar_votacion_de_linchamiento,
                                    datetime.timedelta(minutes=16),
                                    datetime.timedelta(minutes=8),
                                    context={"chat": chat, "partida": partida})
            job_queue.run_repeating(self._finalizar_votacion_de_linchamiento,
                                    datetime.timedelta(minutes=16),
                                    datetime.timedelta(minutes=12),
                                    context={"chat": chat, "partida": partida})
        else:
            job_queue.run_daily(self._iniciar_noche,
                                datetime.time(hour=20),
                                context={"chat": chat, "partida": partida})
            job_queue.run_daily(self._iniciar_anuncios,
                                datetime.time(hour=9),
                                context={"chat": chat, "partida": partida})
            job_queue.run_daily(self._iniciar_votacion_de_linchamiento,
                                datetime.time(hour=13),
                                context={"chat": chat, "partida": partida})
            job_queue.run_daily(self._finalizar_votacion_de_linchamiento,
                                datetime.time(hour=17),
                                context={"chat": chat, "partida": partida})
            # job_queue.run_once()
            # job_queue.run_once()

    @staticmethod
    def _iniciar_noche_lobos(bot, job):

        for jugador in job.context["partida"].jugadores:

            if jugador.personaje.nombre == "un Hombrelobo":
                noche_lobo(bot, job, jugador)

    @staticmethod
    def _iniciar_noche_vidente(bot, job):

        for jugador in job.context["partida"].jugadores:

            if jugador.personaje.nombre == "La Vidente":
                potenciales_victimas = []
                keyboard = []
                text = Lang.get_text("vidente_noche")

                for p_p_victima in job.context["partida"].jugadores:
                    if p_p_victima is not jugador:
                        potenciales_victimas.append(p_p_victima)

                for p_victima in potenciales_victimas:

                    keyboard.append([InlineKeyboardButton(p_victima.nombre_completo_simple,
                                                          callback_data="vidente_observa_a*%s*partida_en*%s")])

                bot.send_message(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    @staticmethod
    def _iniciar_noche(bot, job):
        """ Lanza los mensajes de los primeros turnos de la noche a los jugadores nocturnos. """

        job.context["partida"].dia += 1
        ejecutar_primera_noche = [GameManager._iniciar_noche_lobos, GameManager._iniciar_noche_vidente]
        ejecutar_resto_noches = [GameManager._iniciar_noche_lobos, GameManager._iniciar_noche_vidente]

        if job.context["partida"].dia == 1:
            for f in ejecutar_primera_noche:
                f(bot, job)
        else:
            for f in ejecutar_resto_noches:
                f(bot, job)

    def _iniciar_anuncios(self, bot, job):
        """Lanza los mensajes cuando todo el mundo despierda, anuncia los muertos."""

        partida = job.context["partida"]
        chat = job.context["chat"]

        # Seleccionamos el mensaje apropiado para la cantidad de muertos
        # TODO: el mensaje contiene una lista de los jugadores
        if len(partida.esta_noche_muere) > 1:
            text = Lang.get_text_inserted("amanece_plural",
                                          nombres_y_personajes=Lang.enumerar(
                                              ["%s (%s)" % (jugador.nombre_completo, jugador.personaje.nombre)
                                               for jugador in partida.esta_noche_muere]))
        elif partida.esta_noche_muere:
            text = Lang.get_text_inserted("amanece_singular",
                                          nombre=partida.esta_noche_muere[0].nombre_completo,
                                          personaje=partida.esta_noche_muere[0].personaje.nombre)
        else:
            text = Lang.get_text("amanece_ninguno")

        # Marcamos a los muertos y reiniciamos la lista
        for jugador in partida.esta_noche_muere:
            jugador.personaje.vivo = False
        partida.esta_noche_muere = []

        # Enviamos el mensaje
        bot.send_message(chat_id=chat.id,
                         text=text,
                         parse_mode="Markdown",
                         disable_web_page_preview=True)

        # TODO: ejecutar esto en un método a parte
        # Decimos a la vidente qué ha visto
        for jugador in partida.jugadores:
            if jugador.personaje.nombre == "La Vidente":
                if jugador.personaje.esta_noche_ha_visto_a:
                    bot.send_message(jugador.id,
                                     Lang.get_text_inserted("vidente_ha_visto",
                                                            objetivo=jugador.personaje.esta_noche_ha_visto_a.nombre_completo,
                                                            objetivo_personaje=jugador.personaje.nombre))
                    jugador.personaje.esta_noche_ha_visto_a = None
                # Solo hay una vidente
                break



        victoria = partida.comprobar_victoria()
        if victoria:
            bot.send_message(chat.id,
                             "Han ganado %s" % victoria)

        if DEBUGGING:
            bot.send_message(chat_id=job.context["chat"].id,
                             text="lOS ANUNCIOS se ha inciado correctamente lol")

    def _iniciar_votacion_de_linchamiento(self, bot, job):
        """Envia los mensajes de votación a todos los jugadores vivos."""

        partida = job.context["partida"]
        chat = job.context["chat"]
        partida.linchando = True

        # Avisamos de que empieza la votación
        bot.send_message(chat_id=chat.id,
                         text=Lang.get_text_inserted("comienza_la_votacion",
                                                     player_list=partida.text_player_list()),
                         parse_mode="Markdown",
                         disable_web_page_preview=True)

        # Enviamos un mensaje a los jugadores vivos para que voten
        jugadores_vivos = []
        for jugador in partida.jugadores:
            if jugador.personaje.vivo:
                jugadores_vivos.append(jugador)
        text = Lang.get_text("vota_pofabo")
        for jugador in jugadores_vivos:
            keyboard = []
            tmp = list(jugadores_vivos)
            tmp.remove(jugador)
            for opcion in tmp:
                keyboard.append([InlineKeyboardButton(text=opcion.nombre_completo_simple,
                                                      callback_data="ciudadano_vota_a*%s*partida_en*%s" % (opcion.id, chat.id))])
            bot.send_message(jugador.id,
                             text=text,
                             reply_markup=InlineKeyboardMarkup(keyboard),
                             parse_mode="Markdown")

        if DEBUGGING:
            bot.send_message(chat_id=job.context["chat"].id,
                             text="La iniciar linchamiento se ha inciado correctamente lol")

    def _finalizar_votacion_de_linchamiento(self, bot, job):
        """Contamos los votos y se lincha al más votado :)"""

        partida = job.context["partida"]
        chat = job.context["chat"]
        partida.linchando = False

        # Contamos los votos
        votos = []
        for jugador in partida.jugadores:
            if jugador.personaje.hoy_ha_votado_a:
                votos.append(jugador.personaje.hoy_ha_votado_a)
                jugador.personaje.hoy_ha_votado_a = None

        # Comprobamos si ha votado al menos la mitad de los ciudadanos
        if votos.count(None) > len(votos) // 2:
            bot.send_message(chat_id=chat.id,
                             text=Lang.get_text("fin_linchamiento_insuficientes_votos"))
            return

        # Hacemos el recuento
        recuento = list(set([(n, v) for v in votos for n in [votos.count(v)]]))
        recuento.sort(reverse=True)

        # Comprobamos si hay un empate
        if recuento.__len__() > 1 and recuento[1][0] == recuento[0][0]:
            mas_votado = None
        else:
            mas_votado = recuento[0][1]

        # Decimos quién es el linchado, si no hay mas_votado es un empate.
        if mas_votado:
            mas_votado.personaje.vivo = False
            bot.send_message(chat_id=chat.id,
                             text=Lang.get_text_inserted("fin_linchamiento", linchado=mas_votado.nombre_completo))
        else:
            empates = []
            for recuento_voto in recuento:
                if recuento_voto[0] == recuento[0][0]:
                    empates.append(recuento_voto[1].nombre_completo)
                else:
                    break

            bot.send_message(chat_id=chat.id,
                             text=Lang.get_text_inserted("fin_linchamiento_empate", empates=Lang.enumerar(empates)))

        # Comprobamos si algun bando ha ganado
        victoria = partida.comprobar_victoria()
        if victoria:
            bot.send_message(chat.id,
                             "Han ganado %s" % victoria)

    def _iniciar_busqueda_de_candidatos(self, bot, job):

        partida = job.context["partida"]
        chat = job.context["chat"]
        keyboard = [[""]]

        for jugador in partida.jugadores:

            bot.send_message(jugador.id,
                             Lang.get_text("presentese_candidato"))

    def lobo_mata(self, bot, update, user_data):

        usuario = conseguir_usuario(update, user_data, self.jugadores)
        data_split = update.callback_query.data.split("*")
        id_victima, id_grupo = filter(lambda x: data_split.index(x) % 2 != 0, data_split)
        victima = self.jugadores[int(data_split[1])]
        partida = self.partidas[int(data_split[3])]

        # Comprobamos que haya una partida
        if not partida:
            update.effective_message.edit_text(Lang.get_text("no_game_error"))
            update.callback_query.answer(Lang.get_text("no_game_error"))
            return

        # Nos aseguramos de que no haya votado ya
        if usuario.personaje.esta_noche_ha_matado_a: return

        # Votamos y eliminamos el teclado para que no vuelva a votar.
        usuario.personaje.mata_a(victima)
        update.callback_query.answer(Lang.get_text("objetivo_seleccionado"))
        update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[]]))

        # Comprobamos si el resto de los lobos han votado para eliminar al jugador.
        lobos_vivos = []
        han_votado_todas = True
        for jugador in partida.jugadores:
            if jugador.personaje.nombre == "un Hombrelobo" and jugador.personaje.vivo:
                lobos_vivos.append(jugador)
                if not jugador.personaje.esta_noche_ha_matado_a:
                    han_votado_todas = False
                    bot.send_message(chat_id=jugador.id,
                                     text=Lang.get_text_inserted("x_a_votado_lobos_a_y",
                                                                 x=usuario.nombre_completo,
                                                                 y=victima.nombre_completo),
                                     parse_mode="Markdown",
                                     disable_web_page_preview=True)
        if not han_votado_todas: return

        # Comprobamos quién es la víctima más votada y la marcamos.
        victimas = []
        mas_votada = None
        empate = False
        for lobo in lobos_vivos:
            victimas.append(lobo.personaje.esta_noche_ha_matado_a)
            lobo.personaje.esta_noche_ha_matado_a = None
        for victima in set(victimas):
            if victimas.count(victima) > victimas.count(mas_votada):
                empate = False
                mas_votada = victima
            elif victimas.count(victima) == victimas.count(mas_votada):
                empate = True

        if not empate:
            partida.esta_noche_muere.append(mas_votada)

        # TODO: y si hay empate?
        # TODO: ahora viene la bruja...

    def ciudadano_vota(self, bot, update, user_data):

        usuario = conseguir_usuario(update, user_data, self.jugadores)
        data_split = update.callback_query.data.split("*")
        id_victima, id_grupo = filter(lambda x: data_split.index(x) % 2 != 0, data_split)
        victima = self.jugadores[int(id_victima)]
        partida = self.partidas[int(id_grupo)]

        # Comprobamos si hay una partida
        if not partida:
            update.effective_message.edit_text(Lang.get_text("no_game_error"))
            update.callback_query.answer(Lang.get_text("no_game_error"))
            return

        # Nos aseguramos de que no haya votado ya
        if usuario.personaje.hoy_ha_votado_a:
            return

        # Nos aseguramos de que la partida esté en fase de linchamiento
        if not partida.linchando:
            update.effective_message.edit_reply_markup(InlineKeyboardMarkup([[]]))
            return

        # Votamos y eliminamos el teclado para que no vuelva a votar.
        usuario.personaje.vota_a(victima)
        update.callback_query.answer(Lang.get_text("objetivo_seleccionado"))
        update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[]]))

        # Avisamos en el grupo del voto
        bot.send_message(chat_id=id_grupo,
                         text=Lang.get_text_inserted("x_a_votado_ciudadanos_a_y",
                                                     x=usuario.nombre_completo,
                                                     y=victima.nombre_completo),
                         parse_mode="Markdown",
                         disable_web_page_preview=True)

    def vidente_observa(self, bot, update, user_data):
        usuario = conseguir_usuario(update, user_data, self.jugadores)
        data_split = update.callback_query.data.split("*")
        id_victima, id_grupo = filter(lambda x: data_split.index(x) % 2 != 0, data_split)
        victima = self.jugadores[int(id_victima)]
        partida = self.partidas[int(id_grupo)]

        # Comprobamos si hay una partida
        if not partida:
            update.effective_message.edit_text(Lang.get_text("no_game_error"))
            update.callback_query.answer(Lang.get_text("no_game_error"))
            return

        # Nos aseguramos de que no haya votado ya
        if usuario.personaje.esta_noche_ha_visto_a:
            update.effective_message.edit_reply_markup(InlineKeyboardMarkup([[]]))
            return

        # Votamos y eliminamos el teclado para que no vuelva a votar.
        usuario.personaje.ve_a(victima)
        update.callback_query.answer(Lang.get_text("objetivo_seleccionado"))
        update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([[]]))

    @staticmethod
    def mensaje_no_permitido(bot, update, user_data):
        """Esta funcion castigará los usuarios que hayan reenviado un mensaje del bot."""

        update.effective_message.reply_text("Mensaje no permitido detectado")

    @staticmethod
    def time(bot, update):
        update.effective_message.reply_text(Lang.get_text_inserted("time",
                                                                   time_text=str(datetime.datetime.now().time())),
                                            quote=False)


GameManager = GameManager()
