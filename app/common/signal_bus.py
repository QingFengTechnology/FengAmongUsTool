# coding: utf-8
from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """

    checkUpdateSig = pyqtSignal()
    micaEnableChanged = pyqtSignal(bool)
    serversDownloaded = pyqtSignal()  # 新增：服务器列表下载完成信号


signalBus = None


def getSignalBus():
    global signalBus
    if signalBus is None:
        signalBus = SignalBus()
    return signalBus