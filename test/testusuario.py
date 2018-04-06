# coding=utf-8

import unittest
import usuario


class AnyToDictTests(unittest.TestCase):

    def testdict(self):

        class Tmp: pass

        a = Tmp()
        a.b = "test"
        a.c = Tmp()
        a.c.b = "test2ndlayer"

        result = {"b": "test",
                  "c": {"b": "test2ndlayer"}}

        self.failUnless(usuario.any_to_dict(a) == result)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
