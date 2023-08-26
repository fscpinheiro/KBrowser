import sqlite3
import sys
import psutil
from PyQt5.QtCore import QUrl, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStatusBar,
    QLabel,
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QListWidgetItem,
    QTableWidget,
    QHeaderView
)
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView

from pytube import YouTube
import os
from moviepy.editor import *

class CustomMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 150)

    def showEvent(self, event):
        super().showEvent(event)
        self.timer = QTimer(self)
        self.timer.singleShot(8000, self.close)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Configurações')
        #self.setFixedSize(300, 200)
        self.setMinimumSize(300, 200)

        # Add widgets to layout
        layout = QVBoxLayout(self)
        label = QLabel('Configurações', self)
        layout.addWidget(label)

        self.setWindowTitle('Configurações')
        self.setWindowIcon(QIcon('logo.png'))

        # Adiciona a flag para permitir a maximização da janela
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)

def connect_db(db_file):
    conn = None
    if not os.path.exists(db_file):
        with open(db_file, 'w'):
            pass
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS favorites
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT)''')
        conn.commit()
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)

def handle_favorite_selected(url: str):
    print(f"Função externa. URL : {url}")





class FavoriteDialog(QDialog):
    favorite_selected = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Favoritos')
        self.setWindowIcon(QIcon('logo.png'))
        self.setMinimumSize(600, 400)
        # Adiciona a flag para permitir a maximização da janela
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)
        #conecta ao Banco
        self.editing_favorite_id = None
        self.conn = connect_db("favorites.db")
        # Layout da parte superior
        top_layout = QVBoxLayout()
        top_label = QLabel('Adicionar/Editar Favorito:')
        top_layout.addWidget(top_label)
        name_layout = QHBoxLayout()
        name_label = QLabel('Nome:')
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        top_layout.addLayout(name_layout)
        url_layout = QHBoxLayout()
        url_label = QLabel('URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        top_layout.addLayout(url_layout)
        save_button = QPushButton('Salvar')
        save_button.clicked.connect(self.save_favorite)
        top_layout.addWidget(save_button)
        # Layout da parte inferior
        bottom_layout = QVBoxLayout()
        bottom_label = QLabel('Favoritos Salvos:')
        bottom_layout.addWidget(bottom_label)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID','Nome', 'URL', '', ''])
        self.table.setRowCount(0)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(4, 50)
        header = self.table.horizontalHeader()
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Desabilita a edição da tabela
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        bottom_layout.addWidget(self.table)

        # Adiciona os layouts na janela
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        # Conecta ao banco de dados SQLite
        self.update_favorite_table()

    def delete_favorite(self, row):
        print('Excluindo favorito...')
        try:
            id = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text()
            url = self.table.item(row, 2).text()
            print('Name: '+name)
            print('Url: '+url)
            self.conn.execute('DELETE FROM favorites WHERE id = ?', id)
            self.conn.commit()
            self.update_favorite_table()
            alerta('Favorito excluído com sucesso', QMessageBox.Information)
            print("OK - Favorito excluído")
        except Exception as e:
            alerta(f'Ocorreu um erro ao excluir o favorito: {e}.', QMessageBox.Critical)
            print(f'Ocorreu um erro ao excluir o favorito: {e}.')

    def save_favorite(self):
        name = self.name_input.text()
        url = self.url_input.text()
        id = getattr(self, 'current_favorite_id', -1)

        try:
            c = self.conn.cursor()

            if id == -1:
                # Inserir novo registro
                c.execute('INSERT INTO favorites(name, url) VALUES (?, ?)', (name, url))
                self.conn.commit()
                print("OK - Favorito Salvo")
                alerta('Favorito salvo com sucesso', QMessageBox.Information)
            else:
                # Atualizar registro existente
                c.execute('UPDATE favorites SET name=?, url=? WHERE id=?', (name, url, id))
                self.conn.commit()
                print("OK - Favorito Atualizado")
                alerta('Favorito atualizado com sucesso', QMessageBox.Information)

            self.update_favorite_table()
            self.name_input.setText('')
            self.url_input.setText('')
            self.current_favorite_id = -1

        except Exception as e:
            alerta(f'Ocorreu um erro ao salvar o favorito: {e}.', QMessageBox.Critical)
            print(f'Ocorreu um erro ao salvar o favorito: {e}.')
        finally:
            c.close()

    def edit_favorite(self, favorite):

        try:
            id, name, url = favorite
            self.name_input.setText(name)
            self.url_input.setText(url)
            self.current_favorite_id = id
            self.show()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao carregar favorito: {e}')
            print('Erro', f'Erro ao carregar favorito: {e}')

    def update_favorite_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        c = self.conn.cursor()
        try:
            c.execute('SELECT * FROM favorites')
            favorites = c.fetchall()

            for row, favorite in enumerate(favorites):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(favorite[0])))
                self.table.setItem(row, 1, QTableWidgetItem(favorite[1]))
                self.table.setItem(row, 2, QTableWidgetItem(favorite[2]))
                # Adiciona botão "Excluir"
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon('excluir.png'))
                delete_btn.setToolTip('Excluir favorito')
                delete_btn.clicked.connect(lambda _, row=row: self.delete_favorite(row))
                self.table.setCellWidget(row, 3, delete_btn)
                # Adiciona botão "Editar"
                edit_btn = QPushButton()
                edit_btn.setIcon(QIcon('editar.png'))
                edit_btn.setToolTip('Editar favorito')
                edit_btn.clicked.connect(lambda _, favorite=favorite: self.edit_favorite(favorite))
                self.table.setCellWidget(row, 4, edit_btn)
            # Retorna a lista de tuplas de favoritos
            return favorites
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao buscar favoritos: {e}')
        finally:
            c.close()

    def on_item_double_clicked(self, item):
        url_item = self.table.item(item.row(), 2)
        url = url_item.text()
        print(f'URL: {url} was double clicked')
        #handle_favorite_selected(url)
        self.favorite_selected.emit(url)
        self.close()


class DownloadListDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lista de Downloads')
        #self.setFixedSize(300, 200)
        self.setMinimumSize(300, 200)

        # Add widgets to layout
        layout = QVBoxLayout(self)
        label = QLabel('Lista de Downloads', self)
        layout.addWidget(label)

        self.setWindowTitle('Lista de Downloads')
        self.setWindowIcon(QIcon('logo.png'))

        # Adiciona a flag para permitir a maximização da janela
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)

class MyBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings_dialog = None
        self.favorite_dialog = None
        self.downloadlist_dialog = None

        self.favorite_dialog = FavoriteDialog(self)
        self.favorite_dialog.favorite_selected.connect(self.handle_favorite_selected)

    def initUI(self):
        # Create the navigation buttons
        self.button_back = QPushButton(QIcon('btvoltar.png'), '')
        self.button_back.clicked.connect(self.goBack)
        self.button_back.setToolTip('Voltar')
        self.button_forward = QPushButton(QIcon('btavancar.png'), '')
        self.button_forward.clicked.connect(self.goForward)
        self.button_forward.setToolTip('Avançar')
        self.button_reload = QPushButton(QIcon('refresh.png'), '')
        self.button_reload.clicked.connect(self.reloadPage)
        self.button_reload.setToolTip('Recarregar')
        # Create a line edit and a button to enter the URL
        self.lineedit = QLineEdit(self)
        self.lineedit.returnPressed.connect(self.loadPage)
        # Create the navigation buttons
        self.button_go = QPushButton(QIcon('go.png'), '')
        self.button_go.clicked.connect(self.loadPage)
        self.button_go.setToolTip('Ir para o endereço')
        self.button_download = QPushButton(QIcon('youtube-download.png'), '')
        self.button_download.setToolTip('Download YouTube Video')
        self.button_download.clicked.connect(self.on_download_button_clicked)
        self.button_favorite = QPushButton(QIcon('star.png'), '')
        self.button_favorite.setToolTip('Mostrar meus Favoritos')
        self.button_favorite.clicked.connect(self.showFavorites)
        self.button_downlist = QPushButton(QIcon('downlist.png'), '')
        self.button_downlist.setToolTip('Criar lista de Downloads')
        self.button_downlist.clicked.connect(self.showDownloadList)
        self.button_settings = QPushButton(QIcon('settings.png'), '')
        self.button_settings.setToolTip('Abrir janela de configurações do programa.')
        self.button_settings.clicked.connect(self.showSettings)
        # Add the navigation buttons and line edit to a horizontal layout

        hbox = QHBoxLayout()
        hbox.addWidget(self.button_back)
        hbox.addWidget(self.button_forward)
        hbox.addWidget(self.button_reload)
        hbox.addWidget(self.lineedit)
        hbox.addWidget(self.button_go)
        hbox.addWidget(self.button_download)
        hbox.addWidget(self.button_favorite)
        hbox.addWidget(self.button_downlist)
        hbox.addWidget(self.button_settings)
        # Create a web view to display the page
        self.webview = QWebView(self)
        self.webview.page().urlChanged.connect(self.set_urlbar_text)
        self.webview.setUrl(QUrl("https://www.google.com"))
        # Set the layout and show the form
        layout = QVBoxLayout()
        layout.addLayout(hbox)
        layout.addWidget(self.webview)
        self.setLayout(layout)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('K Browser')
        # Create a status bar
        self.statusBar = QStatusBar(self)
        #self.statusBar.setStyleSheet("QStatusBar{padding-left:8px;padding-top:2px;height:22px;font-size: 10px;}")
        self.statusBar.setStyleSheet("QStatusBar{padding-left:8px;padding-top:2px;height:22px;max-height:32px;font-size: 10px;}")
        self.label_cpu = QLabel(self.statusBar)
        self.label_mem = QLabel(self.statusBar)
        self.label_loading = QLabel(self.statusBar)
        self.statusBar.addWidget(self.label_cpu)
        self.statusBar.addWidget(self.label_mem)
        self.statusBar.addWidget(self.label_loading)
        self.setStatusTip('Carregando...')
        self.layout().addWidget(self.statusBar)
        # Create a timer to periodically update the resource usage
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateResourceUsage)
        self.timer.start(5000)
        self.show()

    def goBack(self):
        self.webview.back()

    def goForward(self):
        self.webview.forward()

    def reloadPage(self):
        self.webview.reload()

    def on_download_button_clicked(self):
        url = self.lineedit.text()
        download_youtube(url)

    def loadPage(self):
        # Get the URL from the line edit and load it
        url = self.lineedit.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.webview.setUrl(QUrl(url))
        self.label_loading.setText('Loading...')
        alerta("Carregando site", QMessageBox.Information)
        # Connect to signals to get the loading progress of the web page
        self.webview.loadProgress.connect(self.onLoadProgress)
        self.webview.loadFinished.connect(self.onLoadFinished)

        self.lineedit.setText(self.webview.url().toString())

    def set_urlbar_text(self, url):
        self.lineedit.setText(url.toString())

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

    def showSettings(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog()
        self.settings_dialog.show()

    def showFavorites(self):
        if not self.favorite_dialog:
            self.favorite_dialog = FavoriteDialog()
        self.favorite_dialog.show()

    def showDownloadList(self):
        if not self.downloadlist_dialog:
            self.downloadlist_dialog = DownloadListDialog()
        self.downloadlist_dialog.show()

    def handle_favorite_selected(self, url: str):
        if not url.startswith('http'):
            url = 'http://' + url
        self.lineedit.setText(url)
        self.webview.setUrl(QUrl(url))

def download_youtube(url):
    print("Salvando video do YouTube")
    urltosave = os.path.normpath("C:\\Users\\fscpinheiro\\\Downloads")
    youtubeObject = YouTube(url)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    if not os.path.exists(urltosave):
        print("diretorio criado")
        os.makedirs(urltosave)
    try:
        print("tentando salvar")
        videofile = youtubeObject.download(urltosave)
        video_name = os.path.basename(videofile)
        print("Nome: "+video_name)
        som_name, extensao = os.path.splitext(video_name)
        som_name = som_name + ".mp3"
        print("AUDIO: "+som_name)
        dir_name = os.path.dirname(videofile)
        print("dir Name: "+dir_name)
        arquivomp4 = os.path.join(dir_name, video_name)
        arquivomp3 = os.path.join(dir_name, som_name)
        MP4ToMP3(arquivomp4, arquivomp3)
    except:
        print("Ocorreu um erro")
    print("Download concluido")

def MP4ToMP3(mp4, mp3):
    print("convertendo")
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()

def alerta(mensagem, tipo):
    msgBox = CustomMessageBox()
    msgBox.setGeometry(300, 300, 400, 200)
    msgBox.setText(mensagem)
    msgBox.setIcon(QMessageBox.Icon(tipo))
    font = QFont()
    font.setPointSize(12)
    msgBox.setFont(font)
    msgBox.setStyleSheet('QMessageBox {background-color: #f8f9fa; color: #212529; border: 1px solid #c3c3c3;}'
                         'QMessageBox QPushButton {background-color: #007bff; color: #fff; padding: 5px 15px; '
                         'border-radius: 3px; font-weight: bold; font-size: 14px;}'
                         'QMessageBox QPushButton:hover {background-color: #0069d9;}')
    msgBox.setStyleSheet("QLabel{min-width:500 px; font-size: 24px;} QPushButton{ width:250px; font-size: 18px; }")
    msgBox.addButton(QPushButton('OK'), QMessageBox.AcceptRole)
    msgBox.exec_()

def eMensagem(mensagem, tipo):
    # Exibe a mensagem do tipo especificado
    msgBox = QMessageBox()
    msgBox.setFixedSize(300, 150)
    msgBox.setText(mensagem)
    msgBox.setIcon(tipo)
    # Define o estilo da caixa de diálogo usando folhas de estilo do Qt
    msgBox.setStyleSheet('QMessageBox {background-color: #f8f9fa; color: #212529; border: 1px solid #c3c3c3;}'
                         'QMessageBox QPushButton {background-color: #007bff; color: #fff; padding: 5px 15px; '
                         'border-radius: 3px; font-weight: bold; font-size: 14px;}'
                         'QMessageBox QPushButton:hover {background-color: #0069d9;}')

    # Define a fonte e o tamanho do texto da caixa de diálogo
    font = QFont()
    font.setPointSize(12)
    msgBox.setFont(font)
    # Define o temporizador para fechar a caixa de diálogo após 8 segundos
    timer = QTimer(msgBox)
    timer.setSingleShot(True)
    timer.timeout.connect(msgBox.close)
    timer.start(6000)


    msgBox.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = MyBrowser()
    sys.exit(app.exec_())