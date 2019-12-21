# -*- coding: utf-8 -*-

import queue
import threading

from enum import Enum
from PyQt5.QtWidgets import QWidget, QMessageBox, QFileDialog, QAbstractItemView
from PyQt5.QtCore import Qt, QStringListModel, pyqtSignal
from PyQt5.QtGui import QIcon
from UI.mainUI import Ui_LFTWidget
from config import configure as config
from LFT import *

#Defined messagebox types
class messageBoxType(Enum):
    scanFinished = 0
    emptyIPOrPort = 1
    emptySourceList = 2
    emptySourcePath = 3
    endServer = 4


class LFTWidget(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        config.readConfig()
        self.initUi()
        self.connectSlot()

    def initUi(self):
        # ui
        self.__ui = Ui_LFTWidget()
        self.__ui.setupUi(self)
        # Set icon
        self.setWindowIcon(QIcon("./icon/LFT.ico"))
        self.__ui.tabWidget.setTabIcon(0,QIcon("./icon/LFT.ico"))
        self.__ui.tabWidget.setTabIcon(1,QIcon("./icon/scan.ico"))
        self.__ui.tabWidget.setTabIcon(2,QIcon("./icon/server.ico"))
        self.__ui.tabWidget.setTabIcon(3,QIcon("./icon/setting.ico"))
        # Send
        self.__lvSendModel = QStringListModel(self)
        self.__ui.lV_Send.setModel(self.__lvSendModel)
        self.__ui.lE_IP_Send.setText(config.Config.client.ip)
        self.__ui.lE_Port_Send.setText(config.Config.client.port)
        # Scan
        self.__lvScanModel = QStringListModel(self)
        self.__ui.lV_Scan.setModel(self.__lvScanModel)
        self.__ui.lV_Scan.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__ui.lE_IP_Scan.setText("192.168.12.1")
        self.__ui.lE_Port_Scan.setText(config.Config.server.port)
        # Server
        self.__ui.pB_End.setDisabled(True)
        self.__lvServerModel = QStringListModel(self)
        self.__ui.lV_Server.setModel(self.__lvServerModel)
        # Setting
        self.__ui.lE_Server_name.setText(config.Config.server.name)
        self.__ui.lE_Server_IP.setText(config.Config.server.ip)
        self.__ui.lE_Server_port.setText(config.Config.server.port)
        self.__ui.lE_Server_save_path.setText(config.Config.server.save_path)
        self.__ui.lE_Client_IP.setText(config.Config.client.ip)
        self.__ui.lE_Client_port.setText(config.Config.client.port)

    def connectSlot(self):
        self.__ui.pB_Add.clicked.connect(self.on__pB_add__clicked)
        self.__ui.pB_Delete.clicked.connect(self.on__pB_Delete__clicked)
        self.__ui.pB_Browse_File.clicked.connect(
            self.on__pB_Browse_File__clicked)
        self.__ui.pB_Browse_Dir.clicked.connect(
            self.on__pB_Browse_Dir__clicked)
        self.__ui.pB_Clear_Send.clicked.connect(
            self.on__pB_Clear_Send__clicked)
        self.__ui.pB_Send.clicked.connect(self.on__pB_Send__clicked)
        self.__ui.pB_Scan.clicked.connect(self.on__pB_Scan__clicked)
        self.__ui.lV_Scan.doubleClicked.connect(self.autoCompleteFormScan)
        self.__ui.pB_Clear_Scan.clicked.connect(
            self.on__pB_Clear_Scan__clicked)
        self.__ui.pB_Start.clicked.connect(self.on__pB_Start__clicked)
        self.__ui.pB_End.clicked.connect(self.on__pB_End__clicked)
        self.__ui.pB_Clear_Server.clicked.connect(
            self.on__pB_Clear_Server__clicked)
        self.__ui.pB_Apply.clicked.connect(self.on__pB_Apply__clicked)
        self.__ui.pB_Reset.clicked.connect(self.on__pB_Reset__clicked)
        self.__ui.pB_Browse_save_path.clicked.connect(
            self.on__pB_Browse_save_path__clicked)
        self.__lvSendModel.dataChanged.connect(self.checkIsEmpty)
        self.showMessageBox.connect(self.showMessageBoxHandler)
        self.updateScanResult.connect(self.updateScanResultHandler)
        self.updateServerLog.connect(self.updateServerLogHandler)

    def scanReporter(self, infoChan):
        info = infoChan.get()
        while info != "__finished__":
            info = info[1]+"   "+info[4]
            self.updateScanResult.emit(info)
            info = infoChan.get()
        else:
            self.showMessageBox.emit(messageBoxType.scanFinished)
            self.__ui.pB_Scan.setEnabled(True)

    def serverlogger(self, infoChan):
        info = infoChan.get()
        while info != "__finished__":
            if len(info) == 10:
                info = info[0]+" "+info[1]+" "+info[4]+" "+info[8]+info[9]
            else:
                info = " ".join(info)
            self.updateServerLog.emit(info)
            info = infoChan.get()
        else:
            self.showMessageBox.emit(messageBoxType.endServer)

    # Signal
    showMessageBox = pyqtSignal(messageBoxType)
    updateScanResult = pyqtSignal(str)
    updateServerLog = pyqtSignal(str)

    # Slots
    # Rewrite event
    def closeEvent(self, QCloseEvent):
        if hasattr(self, "_LFTWidget__serverControlChan") and self.__serverControlChan.empty():
            reply = QMessageBox.question(self, "Warning", "Server is still running, stop it?",
                                         QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.__serverControlChan.put("kill")
                QCloseEvent.accept()
            else:
                QCloseEvent.ignore()
                return
        else:
            QCloseEvent.accept()

    # Handler
    def updateScanResultHandler(self, info):
        self.__lvScanModel.insertRow(self.__lvScanModel.rowCount())
        index = self.__lvScanModel.index(
            self.__lvScanModel.rowCount()-1, 0)
        self.__lvScanModel.setData(index, info)

    def updateServerLogHandler(self, info):
        self.__lvServerModel.insertRow(self.__lvServerModel.rowCount())
        index = self.__lvServerModel.index(
            self.__lvServerModel.rowCount()-1, 0)
        self.__lvServerModel.setData(index, info)

    def showMessageBoxHandler(self, type):
        if type == messageBoxType.scanFinished:
            QMessageBox.information(
                None, "Infomation", "Scan servers finished")
        elif type == messageBoxType.emptyIPOrPort:
            QMessageBox.warning(
                self, "Warning", "IP or port cannot be empty!")
        elif type == messageBoxType.emptySourceList:
            QMessageBox.warning(
                self, "Warning", "Please enter source first!")
        elif type == messageBoxType.emptySourcePath:
            QMessageBox.warning(
                self, "Warning", "Source cannot be empty!!")
        elif type == messageBoxType.endServer:
            QMessageBox.information(
                None, "Infomation", "Server now stopped")

    # --Client
    def autoCompleteFormScan(self, index):
        data = self.__lvScanModel.data(index, Qt.DisplayRole)
        IPAddr = data.split()[1]
        IP = IPAddr.split(":")[0]
        port = IPAddr.split(":")[1]
        self.__ui.lE_IP_Send.setText(IP)
        self.__ui.lE_Port_Send.setText(port)
        self.__ui.tabWidget.setCurrentIndex(0)

    def on__pB_add__clicked(self):
        self.__lvSendModel.insertRow(self.__lvSendModel.rowCount())
        index = self.__lvSendModel.index(self.__lvSendModel.rowCount()-1, 0)
        self.__lvSendModel.setData(index, "Source path")
        self.__ui.lV_Send.setCurrentIndex(index)
        self.__ui.lV_Send.edit(index)
    # If it is empty, give a warning and delete it
    def checkIsEmpty(self):
        if self.__lvSendModel.data(self.__ui.lV_Send.currentIndex(), Qt.DisplayRole) == "":
            self.showMessageBox.emit(messageBoxType.emptySourcePath)
            self.on__pB_Delete__clicked()
    # Delete current row
    def on__pB_Delete__clicked(self):
        self.__lvSendModel.removeRow(self.__ui.lV_Send.currentIndex().row())

    def on__pB_Browse_File__clicked(self):
        filePath, _ = QFileDialog.getOpenFileName()
        if filePath != "":
            self.__lvSendModel.insertRow(self.__lvSendModel.rowCount())
            index = self.__lvSendModel.index(
                self.__lvSendModel.rowCount()-1, 0)
            self.__lvSendModel.setData(index, filePath)
            self.__ui.lV_Send.setCurrentIndex(index)

    def on__pB_Browse_Dir__clicked(self):
        dirPath = QFileDialog.getExistingDirectory()
        if dirPath != "":
            self.__lvSendModel.insertRow(self.__lvSendModel.rowCount())
            index = self.__lvSendModel.index(
                self.__lvSendModel.rowCount()-1, 0)
            self.__lvSendModel.setData(index, dirPath)
            self.__ui.lV_Send.setCurrentIndex(index)
    # Clear rows
    def on__pB_Clear_Send__clicked(self):
        self.__lvSendModel.removeRows(0, self.__lvSendModel.rowCount())

    def on__pB_Send__clicked(self):
        ip = self.__ui.lE_IP_Send.text()
        port = self.__ui.lE_Port_Send.text()
        # Check if ip and port is empty
        if ip == "" or port == "":
            self.showMessageBox.emit(messageBoxType.emptyIPOrPort)
            return
        paths = self.__lvSendModel.stringList()
        # Check if path list is empty
        if not paths:
            self.showMessageBox.emit(messageBoxType.emptySourceList)
            return
        # Send files or dirs one by one
        for i, path in enumerate(paths):
            infoChan = queue.Queue(10)
            index = self.__lvSendModel.index(i, 0)
            self.__lvSendModel.setData(index, LFTSend(path, ip, port))

    # --Scan
    def on__pB_Scan__clicked(self):
        ips = self.__ui.lE_IP_Scan.text()
        ports = self.__ui.lE_Port_Scan.text()
        if ips == "" or ports == "":
            self.showMessageBox.emit(messageBoxType.emptyIPOrPort)
            return
        infoChan = queue.Queue(10)
        scanner = threading.Thread(target=LFTScan, args=[infoChan, ips, ports])
        reporter = threading.Thread(target=self.scanReporter, args=[infoChan])
        reporter.start()
        scanner.start()
        self.__ui.pB_Scan.setDisabled(True)

    def on__pB_Clear_Scan__clicked(self):
        self.__lvScanModel.removeRows(0, self.__lvScanModel.rowCount())

    # --Server
    def on__pB_Start__clicked(self):
        ip = config.Config.server.ip
        port = config.Config.server.port
        name = config.Config.server.name
        savePath = config.Config.server.save_path
        if ip == "" or port == "" or name == "" or savePath == "":
            ip = "0.0.0.0"
            port = "6981"
            name = "LFT-Server"
            savePath = "./receive"
        self.__serverControlChan = queue.Queue(1)
        infoChan = queue.Queue(10)
        server = threading.Thread(
            target=LFTServer, args=[infoChan, self.__serverControlChan, ip, port, name, savePath])
        logger = threading.Thread(target=self.serverlogger, args=[infoChan])
        server.daemon = True
        logger.daemon = True
        logger.start()
        server.start()
        self.__ui.pB_Start.setDisabled(True)
        self.__ui.pB_End.setEnabled(True)

    def on__pB_End__clicked(self):
        self.__serverControlChan.put("kill")
        self.on__pB_Clear_Server__clicked()
        self.__ui.pB_End.setDisabled(True)
        self.__ui.pB_Start.setEnabled(True)

    def on__pB_Clear_Server__clicked(self):
        self.__lvServerModel.removeRows(0, self.__lvServerModel.rowCount())

    # --Setting
    def on__pB_Apply__clicked(self):
        config.Config.server.name = self.__ui.lE_Server_name.text()
        config.Config.server.ip = self.__ui.lE_Server_IP.text()
        config.Config.server.port = self.__ui.lE_Server_port.text()
        config.Config.server.save_path = self.__ui.lE_Server_save_path.text()
        config.Config.client.ip = self.__ui.lE_Client_IP.text()
        config.Config.client.port = self.__ui.lE_Client_port.text()
        config.saveConfig()

    def on__pB_Reset__clicked(self):
        config.initConfig()
        config.readConfig()
        self.__ui.lE_Server_name.setText(config.Config.server.name)
        self.__ui.lE_Server_IP.setText(config.Config.server.ip)
        self.__ui.lE_Server_port.setText(config.Config.server.port)
        self.__ui.lE_server_save_path.setText(config.Config.server.save_path)
        self.__ui.lE_Client_IP.setText(config.Config.client.ip)
        self.__ui.lE_Client_port.setText(config.Config.client.port)

    def on__pB_Browse_save_path__clicked(self):
        dirPath = QFileDialog.getExistingDirectory()
        if dirPath != "":
            self.__ui.lE_Server_save_path.setText(dirPath)
