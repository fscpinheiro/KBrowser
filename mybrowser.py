import psutil
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStatusBar,
    QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage


class MyBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a line edit and a button to enter the URL
        self.lineedit = QLineEdit(self)
        self.lineedit.returnPressed.connect(self.loadPage)
        self.button = QPushButton('Go', self)
        self.button.clicked.connect(self.loadPage)

        # Create the navigation buttons
        self.button_go = QPushButton(QIcon('go.png'), '')
        self.button_download = QPushButton(QIcon('download.png'), '')
        self.button_favorite = QPushButton(QIcon('star.png'), '')
        self.button_downlist = QPushButton(QIcon('downlist.png'), '')
        self.button_settings = QPushButton(QIcon('settings.png'), '')

        # Add the navigation buttons and line edit to a horizontal layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.lineedit)
        hbox.addWidget(self.button_go)
        hbox.addWidget(self.button_download)
        hbox.addWidget(self.button_favorite)
        hbox.addWidget(self.button_downlist)
        hbox.addWidget(self.button_settings)

        # Create a web view to display the page
        self.webview = QWebView(self)

        # Set the layout and show the form
        layout = QVBoxLayout()
        layout.addLayout(hbox)
        layout.addWidget(self.webview)
        self.setLayout(layout)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('K Browser')

        # Create a status bar
        self.statusBar = QStatusBar(self)
        self.statusBar.setStyleSheet("QStatusBar{padding-left:8px;padding-top:2px;height:22px;font-size: 10px;}")
        self.label_cpu = QLabel(self.statusBar)
        self.label_mem = QLabel(self.statusBar)
        self.label_loading = QLabel(self.statusBar)
        self.statusBar.addPermanentWidget(self.label_cpu)
        self.statusBar.addPermanentWidget(self.label_mem)
        self.statusBar.addWidget(self.label_loading)
        self.setStatusBar(self.statusBar)

        # Create a timer to periodically update the resource usage
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateResourceUsage)
        self.timer.start(5000)

        self.show()

    def loadPage(self):
        # Get the URL from the line edit and load it
        url = self.lineedit.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.webview.setUrl(QUrl(url))
        self.label_loading.setText('Loading...')

        # Connect to signals to get the loading progress of the web page
        self.webview.loadProgress.connect(self.onLoadProgress)
        self.webview.loadFinished.connect(self.onLoadFinished)

    def onLoadProgress(self, progress):
        self.label_loading.setText('Loading... ' + str(progress) + '%')

    def onLoadFinished(self):
        self.label_loading.setText('Done')

    def updateResourceUsage(self):
        # Get the system resource usage
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()

        # Update the labels in the status bar
        self.label_cpu.setText(f'CPU: {cpu}%')
        self.label_mem.setText(f'MEM: {mem.percent}%')