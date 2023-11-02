from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel

from .Client import Client


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(438, 205)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.srcImage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.srcImage.sizePolicy().hasHeightForWidth())
        self.srcImage.setSizePolicy(sizePolicy)
        self.srcImage.setObjectName("srcImage")
        self.verticalLayout.addWidget(self.srcImage)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.dstImage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dstImage.sizePolicy().hasHeightForWidth())
        self.dstImage.setSizePolicy(sizePolicy)
        self.dstImage.setObjectName("dstImage")
        self.verticalLayout_2.addWidget(self.dstImage)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.diffImage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.diffImage.sizePolicy().hasHeightForWidth())
        self.diffImage.setSizePolicy(sizePolicy)
        self.diffImage.setObjectName("diffImage")
        self.verticalLayout_3.addWidget(self.diffImage)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.similarity = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.similarity.sizePolicy().hasHeightForWidth())
        self.similarity.setSizePolicy(sizePolicy)
        self.similarity.setObjectName("similarity")
        self.horizontalLayout_3.addWidget(self.similarity)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.thresh = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thresh.sizePolicy().hasHeightForWidth())
        self.thresh.setSizePolicy(sizePolicy)
        self.thresh.setObjectName("thresh")
        self.horizontalLayout_4.addWidget(self.thresh)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "源图片"))
        self.srcImage.setText(_translate("MainWindow", "<SrcImage>"))
        self.label_2.setText(_translate("MainWindow", "截屏区域"))
        self.dstImage.setText(_translate("MainWindow", "<DstImage>"))
        self.label_3.setText(_translate("MainWindow", "DIFF"))
        self.diffImage.setText(_translate("MainWindow", "<diffImage>"))
        self.label_4.setText(_translate("MainWindow", "相似度:"))
        self.similarity.setText(_translate("MainWindow", "TextLabel"))
        self.label_5.setText(_translate("MainWindow", "二值化阈值"))
        self.thresh.setText(_translate("MainWindow", "TextLabel"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setBaseSize(400, 150)

        # listen port 65534
        self.port = 65534
        self.tcpClient = Client(self.port)
        self.title_text = f'Image Comparator :: port {self.port}  |  '
        self.setWindowTitle(self.title_text)
        self.tcpClient.receivedImage.connect(self.receiveImage)
        self.tcpClient.receivedText.connect(self.receiveText)

        self.tcpClient.connected.connect(self.onConnected)
        self.tcpClient.disconnected.connect(self.onDisconnected)
        self.tcpClient.noConnection.connect(self.onNoConnection)

    def onConnected(self):
        self.setWindowTitle(self.title_text + 'connected')

    def onDisconnected(self):
        self.setWindowTitle(self.title_text + 'disconnected')

    def onNoConnection(self):
        self.setWindowTitle(self.title_text + 'no connection')

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.tcpClient.stop()
        super().closeEvent(a0)

    def receiveImage(self, name, img: QPixmap):
        label: QLabel = getattr(self.ui, name)
        # adjust label size
        label.setFixedSize(img.size())
        label.setPixmap(img)

    def receiveText(self, key, value):
        label = getattr(self.ui, key)
        label.setText(value)
