# coding=utf-8

from lang import Lang


def objetivo_valido(objetivo, vivo=True):

    # assert isinstance(objetivo, Usuario), "El objetivo tiene que ser un personaje"
    assert objetivo.personaje.vivo == vivo, "El objetivo tiene que estar vivo."

    return True


class Personaje:

    nombre = "ERR. PERSONAJE SIN NOMBRE"
    bando = "aldeanos"
    nocturno = False
    turnos_nocturnos_anteriores = []

    def __init__(self, *args, **kwargs):
        """Base para los personajes"""

        self.de_la_partida = kwargs.get("de_la_partida")
        self.alguacil = kwargs.get("alguacil", False)
        self.vivo = kwargs.get("vivo", True)
        self.hoy_ha_votado_a = kwargs.get("hoy_ha_votado_a", None)
        self.mensajes_enviados = 0
        self.longutud_total_de_mensajes = 0
        self.motivo_de_muerte = None
        self.es_alguacil = False

        # assert self.de_la_partida is not None, "El personaje tiene que pertenecer a alguna partida"

    def vota_a(self, objetivo):

        assert objetivo_valido(objetivo)
        self.hoy_ha_votado_a = objetivo

        return True

    def muere(self, motivo):

        self.vivo = False
        self.motivo_de_muerte = motivo

        return True

    def _text_explicacion(self):

        return Lang.get_text("explicacion_inicial-%s" % self.nombre)

    def mensajes_iniciales(self, **kargs):

        return [self._text_explicacion()]


class Aldeano(Personaje):

    nombre = "un Aldeano"
    maximo_por_baraja = -1
    minimo_por_baraja = 0
    minimo_jugadores = 0

    def __init__(self, *args, **kwargs):

        Personaje.__init__(self, *args, **kwargs)


class Lobo(Personaje):

    nombre = "un Hombrelobo"
    maximo_por_baraja = -1
    minimo_por_baraja = 2
    minimo_jugadores = 0
    bando = "lobos"
    nocturno = True

    def __init__(self, *args, **kwargs):

        Personaje.__init__(self, nocturno=True, bando="lobos", *args, **kwargs)

        self.esta_noche_ha_matado_a = None

    @staticmethod
    def accion_nocturna(partida):

        text = Lang.get_text("lobos_noche")
        potenciales_victimas = []

        for potencial_potencial_victima in partida.jugadores:

            if potencial_potencial_victima.personaje.bando != "lobos":
                potenciales_victimas.append(potencial_potencial_victima)

        return text, potenciales_victimas

    def mata_a(self, objetivo):

        assert objetivo_valido(objetivo)
        self.esta_noche_ha_matado_a = objetivo

        return True

    @staticmethod
    def _text_manada(lista_manada):

        return Lang.get_text_inserted("manada", lista_manada=lista_manada)

    def mensajes_iniciales(self, **kwargs):

        return [self._text_explicacion(), self._text_manada(kwargs.get("lista_manada"))]


class Vidente(Personaje):

    nombre = "La Vidente"
    maximo_por_baraja = 1
    minimo_por_baraja = 0
    minimo_jugadores = 0
    nocturno = True

    def __init__(self, *args, **kwargs):

        Personaje.__init__(self, nocturno=True, *args, **kwargs)
        self.esta_noche_ha_visto_a = None

    def ve_a(self, objetivo):

        assert objetivo_valido(objetivo)
        self.esta_noche_ha_visto_a = objetivo


class Bruja(Personaje):

    nombre = "La Bruja"
    maximo_por_baraja = 1
    minimo_por_baraja = 0
    minimo_jugadores = 0
    nocturno = True
    turnos_nocturnos_anteriores = [Lobo]

    def __init__(self, *args, **kwargs):

        Personaje.__init__(self, nocturno=True, *args, **kwargs)
        self.pociones_curar = 1
        self.pociones_matar = 1
        self.esta_noche_ha_curado_a = None
        self.esta_noche_ha_matado_a = None

    def curar(self, objetivo):

        assert self.pociones_curar > 0, "No quedan pociones para curar"
        assert objetivo_valido(objetivo)

        self.esta_noche_ha_curado_a = objetivo

    def matar(self, objetivo):

        assert self.pociones_matar > 0, "No quedan pociones para matar"
        assert objetivo_valido(objetivo)

        self.esta_noche_ha_matado_a = objetivo


class Cazador(Personaje):  # TODO: y lo de que mata a alguien qué?

    nombre = "El Cazador"
    maximo_por_baraja = 1
    minimo_por_baraja = 0
    minimo_jugadores = 0

    def __init__(self, *args, **kargs):

        Personaje.__init__(self, *args, **kargs)


NOMBRE_A_OBJETO = {"un Aldeano": Aldeano, "La Bruja": Bruja, "La Vidente": Vidente, "un Hombrelobo": Lobo,
                   "Cazador": Cazador}
PERSONAJES_DISPONIBLES = [Aldeano, Lobo]
BANDO_LOBOS = [Lobo]
BANDO_ALDEANOS = [Aldeano]
BARAJA_BASE = [Lobo, Lobo, Vidente, Bruja, Cazador, Aldeano, Aldeano]
