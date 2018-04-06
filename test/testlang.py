# coding=utf-8

import unittest
from lang.lang import Lang


class EnumerarTests(unittest.TestCase):

    def testun_elemento(self):

        resultado = Lang.enumerar(["hola"])
        self.assertEqual(resultado, "hola", "El resulado no es el esperado para un elemento")

    def testdos_elemntos(self):

        resultado = Lang.enumerar(["hola", "lol"])
        self.assertEqual(resultado, "hola y lol", "El resulado no es el esperado para dos elementos")

    def testtres_elementos(self):

        resultado = Lang.enumerar(["hola", "lol", "no"])
        self.assertEqual(resultado, "hola, lol y no", "El resulado no es el esperado para tres elementos")

    def testcuatro_elementos(self):

        resultado = Lang.enumerar(["hola", "lol", "no", "creo"])
        self.assertEqual(resultado, "hola, lol, no y creo", "El resulado no es el esperado para cuatro elementos")

    def testlanza_error_cuando_no_es_text(self):

        self.assertRaises(AssertionError, Lang.enumerar, [None])


def main():
    unittest.main()


if __name__ == "__main__":
    main()
