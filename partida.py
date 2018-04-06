# coding=utf-8

import random, constantes
from credenciales import DEBUGGING
from lang.lang import Lang
from personajes import BANDO_ALDEANOS, BANDO_LOBOS, PERSONAJES_DISPONIBLES


class Partida:

    def __init__(self, creada_por, *args, **kwargs):

        self.jugadores = []
        self.creada_por = creada_por
        self.narrador = kwargs.get("narrador")
        self.alguacil = kwargs.get("alguacil")
        self.baraja = []
        self.dia = 0
        self.esta_noche_muere = []
        self.partida_empezada = False
        self.linchando = False

    def _repartir_cartas(self):

        n_jugadores = len(self.jugadores)

        if not DEBUGGING:
            assert n_jugadores >= constantes.MINIMO_JUGADORES, "Mínimo de jugadores no alcanzado"

        self._hacer_una_baraja()
        baraja = list(self.baraja)
        random.shuffle(baraja)

        assert len(baraja) >= len(self.jugadores), "Hay más jugadores que cartas."

        for n in range(n_jugadores):
            self.jugadores[n].personaje = baraja[n]()

    def _text_baraja(self):

        if not self.baraja:
            return "\nNo se ha hecho una baraja todavía"
        else:
            txt = "\n" + Lang.get_text("baraja") + "\n"
            for personaje in self.baraja:
                txt += "\n" + personaje.nombre
            return txt

    def _text_lista_manada(self):

        txt = ""
        cuentan_como_manada = ["un Hombrelobo"]

        for jugador in self.jugadores:
            if jugador.personaje.nombre in cuentan_como_manada:
                txt += "\n%s" % jugador.nombre_completo

        return txt

    def _personaje_puede_entrar(self, personaje):
        """Para comprobar si el personaje puede entrar en la baraja"""

        if personaje.maximo_por_baraja != -1 and personaje.maximo_por_baraja <= self.baraja.count(personaje):
            return False

        if personaje.minimo_jugadores > len(self.jugadores):
            return False

        return True

    def _hacer_una_baraja(self):

        bandos = {"lobos":0, "aldeanos":0}
        cartas_necesarias = len(self.jugadores)

        for personaje in PERSONAJES_DISPONIBLES:
            for n in range(personaje.minimo_por_baraja):
                bandos[personaje.bando] += 1
                self.baraja.append(personaje)

        while not bandos["aldeanos"]:
            nuevo_personaje = BANDO_ALDEANOS[random.randint(0, len(BANDO_ALDEANOS) - 1)]
            if self._personaje_puede_entrar(nuevo_personaje):
                self.baraja.append(nuevo_personaje)
                bandos[nuevo_personaje.bando] += 1

        while cartas_necesarias > len(self.baraja):
            if bandos["lobos"] / float(bandos["aldeanos"]) < constantes.LOBOS_POR_CIUDADANO:
                nuevo_personaje = BANDO_LOBOS[random.randint(0, random.randint(0, len(BANDO_LOBOS) - 1))]
            else:
                nuevo_personaje = BANDO_ALDEANOS[random.randint(0, random.randint(0, len(BANDO_ALDEANOS) - 1))]
            if self._personaje_puede_entrar(nuevo_personaje):
                self.baraja.append(nuevo_personaje)
                bandos[nuevo_personaje.bando] += 1

    def comprobar_victoria(self):

        personajes_vivos = []

        for jugador in self.jugadores:
            if jugador.personaje.vivo:
                personajes_vivos.append(jugador.personaje)

        if not personajes_vivos:
            return True
        elif len(personajes_vivos) == 1:
            return personajes_vivos[0].bando

        for n in range(1, len(personajes_vivos)):
            if personajes_vivos[0].bando != personajes_vivos[n].bando:
                return False

        return personajes_vivos[0].bando

    def text_player_list(self):  # TODO soportar post-game y también langs

        txt = u""
        if not self.partida_empezada:
            if self.jugadores:
                txt = Lang.get_text("player_list")

                for jugador in self.jugadores:
                    txt += u"\n" + jugador.nombre_completo
        else:
            txt = Lang.get_text("player_list")

            for jugador in self.jugadores:
                if jugador.personaje.vivo:
                    txt += u"\n" + jugador.nombre_completo
            for jugador in self.jugadores:
                if not jugador.personaje.vivo:
                    txt += u"\n" + jugador.nombre_completo_simple + u" ☠️ " + jugador.personaje.nombre

        return txt

    def iniciar_partida(self, bot, grupo):  # todo: nombrar alguacil al que tiene que serlo

        self._repartir_cartas()
        lista_manada = self._text_lista_manada()
        self.partida_empezada = True

        for jugador in self.jugadores:
            jugador.lanzar_explicacion_inicial(bot, lista_manada=lista_manada)

        bot.send_message(text=Lang.get_text_inserted("game_started", baraja=self._text_baraja()),
                         chat_id=grupo.id,
                         parse_mode="Markdown",
                         disable_web_page_preview=True)
