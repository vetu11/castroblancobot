# coding=utf-8

import json
from partida import Partida
from usuario import Usuario


def conseguir_chat(update, chat_data):

    if "chat_castroblanco" in chat_data:
        return chat_data["chat_castroblanco"]

    else:
        try:
            with open("grupos/%s.chat" % update.effective_user.id) as f:
                chat = Grupo(**json.load(f))
        except:
            chat = Grupo(id=update.effective_chat.id)
        chat_data["chat_castroblanco"] = chat
        return chat


class Chat:

    def __init__(self, **kwargs):

        self.id = kwargs.get("id")

        assert self.id != None, "La id no puede ser None"


class Grupo(Chat):

    def __init__(self, **kwargs):

        Chat.__init__(self, **kwargs)
        self.partida = kwargs.get("partida")
        self.ultimo_alguacil = kwargs.get("ultimo_alcuacil")

        if type(self.partida) == dict:
            self.partida = Partida(**self.partida)

        if type(self.ultimo_alguacil) == dict:
            self.ultimo_alguacil = Usuario(**self.ultimo_alguacil)

    def migrar_chat(self, update):

        assert update.message.migrate_from_chat_id == self.id, "Id inválida"

        self.id = update.message.migrate_to_chat_id

        return True

    def nuevo_alguacil(self, usuario=None):

        self.ultimo_alguacil = usuario
