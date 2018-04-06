# coding=utf-8

import json
from personajes import NOMBRE_A_OBJETO


def conseguir_usuario(update, user_data, libro):

    if "usuario_castroblanco" in user_data:
        return user_data["usuario_castroblanco"]

    else:
        try:
            with open("users/%s.user" % update.effective_user.id) as f:
                usuario = Usuario(**json.load(f))
        except IOError:
            usuario = Usuario(id=update.effective_user.id,  # TODO: esto se puede pasar como un dicc?
                              nombre_de_usuario=update.effective_user.username,
                              nombre=update.effective_user.first_name,
                              apellidos=update.effective_user.last_name)
        user_data["usuario_castroblanco"] = usuario
        usuario.actualizar_nombre(update)
        libro[usuario.id] = usuario
        return usuario


def any_to_dict(self):

    try:
        first_dict = self.__dict__
    except: raise "No se puede pasar a dict, es una istancia?"

    for key in first_dict:

        try:
            new_thing = any_to_dict(first_dict[key])
            first_dict[key] = new_thing
        except: pass

    return first_dict


class Usuario:

    def __init__(self, *args, **kwargs):
        """Combinación de usuario de Telegram y de el juego."""

        self.id = kwargs.get("id")
        self.personaje = kwargs.get("personaje")
        self.nombre_de_usuario = kwargs.get("nombre_de_usuario")
        self.nombre = kwargs.get("nombre")
        self.apellidos = kwargs.get("apellidos")
        self.nombre_completo = kwargs.get("nombre_completo")
        self.perdones = kwargs.get("perdones", 0.5)

        self.actualizar_nombre(kwargs.get("update"))

        assert self.id is not None, "ID inválida (None)"
        assert self.nombre is not None, "Nombre inválido (None)"

        if type(self.personaje) == dict : # not isinstance(self.personaje, Personaje) and self.personaje != None
            self.personaje = NOMBRE_A_OBJETO[self.personaje["nombre"]](**self.personaje)

        self.guardar()

    def _crear_nombre_completo(self):
        if self.nombre_de_usuario:
            if self.apellidos:
                self.nombre_completo = "[%s %s](t.me/%s)" % (self.nombre, self.apellidos, self.nombre_de_usuario)
                self.nombre_completo_simple = self.nombre + " " + self.apellidos
            else:
                self.nombre_completo = "[%s](t.me/%s)" % (self.nombre, self.nombre_de_usuario)
                self.nombre_completo_simple = self.nombre
        else:
            if self.apellidos:
                self.nombre_completo_simple = self.nombre_completo = self.nombre + " " + self.apellidos
            else:
                self.nombre_completo_simple = self.nombre_completo = self.nombre
        return True

    def actualizar_nombre(self, update):

        if not update:
            if not self.nombre_completo: self._crear_nombre_completo()
            return False

        self.nombre_de_usuario = update.effective_user.username
        self.nombre = update.effective_user.first_name
        self.apellidos = update.effective_user.last_name
        self._crear_nombre_completo()

        return True

    def guardar(self):

        with open("users/%s.user" % self.id, "w") as f:
            json.dump(any_to_dict(self), f, indent=2)

    def lanzar_explicacion_inicial(self, bot, **kargs):

        texts = self.personaje.mensajes_iniciales(**kargs)

        for text in texts:
            bot.send_message(text=text,
                             chat_id=self.id,
                             parse_mode="Markdown",
                             disable_web_page_preview=True)
