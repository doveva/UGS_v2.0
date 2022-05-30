#!/usr/bin/env python
class UserException(Exception):
    """ Пользовательское исключение
    """

    def __init__(self, *txt):
        if txt:
            self.txt = txt[0]
        else:
            self.txt = None

    def __str__(self):
        if self.txt:
            return "\nОшибка:\n{0}".format(self.txt)
        else:
            return "\nОшибка"
