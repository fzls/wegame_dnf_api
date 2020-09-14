class Object():
    def __init__(self, fromDict=None):
        if fromDict is None:
            fromDict = {}
        self.__dict__ = fromDict

    def __str__(self):
        return str(self.__dict__)


def uin2qq(uin):
    return str(uin)[1:].lstrip('0')
