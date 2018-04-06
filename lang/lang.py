# coding=utf-8

import json
from credenciales import DEBUGGING, VERSION


class Lang:

    def __init__(self):

        with open("lang/es-ES.json") as f:
            self.es_ES = json.load(f)

    def get_text(self, text, lang="es-ES"):
        txt = self.es_ES[text]
        if DEBUGGING and len(txt) < 200:
            txt += u"*MODO DE PRUEBA versión %s*\n" % VERSION

        return txt

    def get_text_inserted(self, text, lang="es-ES", **kwargs):

        return self.es_ES[text].format(**kwargs)

    def enumerar(self, lst, lang="es_ES"):

        ander = self.es_ES["&"]
        txt = ""
        for e in lst:
            assert type(e) == str
            txt = txt.format("{1}", "{2}", "{2}")
            txt += "%s{0}" % e
        txt = txt.format("", " %s " % ander, ", ")

        return txt


Lang = Lang()
