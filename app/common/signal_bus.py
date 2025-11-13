# coding: utf-8
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """

    checkUpdateSig = pyqtSignal()
    micaEnableChanged = pyqtSignal(bool)


signalBus = None


def getSignalBus():
    global signalBus
    if signalBus is None:
        signalBus = SignalBus()
    return signalBus