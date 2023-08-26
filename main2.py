import tkinter as tk
from PIL import Image, ImageTk
import webbrowser
import webview
import requests

root = tk.Tk()
root.title("Navegador")
webview.create_window("Navegador", width=800, height=600, resizable=True)

def load_website(url):
    # Envia uma requisição GET para a URL e obtém a resposta
    response = requests.get(url)
    # Converte o conteúdo HTML da resposta em uma string
    content = response.content.decode("utf-8")
    # Define o conteúdo HTML na janela da webview
    webview.set_html(content, base_uri=response.url)
    webview_window = webview.windows[0]
    webview_window.set_parent(page_frame.winfo_id())


def go_to_website(url):
    webview.windows[0].load_url(url)
    webview.pack(expand=True, fill="both", in_=page_frame)

def show_settings():
    screen1 = tk.Toplevel()
    screen1.title("Configurações")
    text = tk.Label(screen1, text="Esta é a tela de configurações")
    text.pack()

def show_downlist():
    window = tk.Toplevel(root)
    window.geometry("500x300")
    frame = tk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)
    label = tk.Label(frame, text="Gerenciador de Downloads")
    label.pack(pady=50)
    button = tk.Button(frame, text="Fechar", command=window.destroy)
    button.pack(pady=10)
    img = tk.PhotoImage(file="media.png")
    button.config(image=img, compound=tk.TOP)
    window.mainloop()


def open_favorites():
    modal = tk.Toplevel()
    modal.geometry("400x300")
    modal.title("Modal Window")
    # Adicione aqui o conteúdo da janela modal
    modal.grab_set()
    modal.focus_set()
    modal.wait_window()

# Carregando o ícone de atualização
go_icon = Image.open("go.png")
go_icon = go_icon.resize((32, 32))
go_icon = ImageTk.PhotoImage(go_icon)
download_icon = Image.open("download.png")
download_icon = download_icon.resize((32,32))
download_icon = ImageTk.PhotoImage(download_icon)
favorite_icon = Image.open("star.png")
favorite_icon = favorite_icon.resize((32,32))
favorite_icon = ImageTk.PhotoImage(favorite_icon)
downlist_icon = Image.open("downlist.png")
downlist_icon = downlist_icon.resize((32,32))
downlist_icon = ImageTk.PhotoImage(downlist_icon)
settings_icon = Image.open("settings.png")
settings_icon = settings_icon.resize((32,32))
settings_icon = ImageTk.PhotoImage(settings_icon)

# Criando o frame principal
main_frame = tk.Frame(root)
main_frame.pack(side="top", fill="both", expand=True)

# Criando a barra de endereço
address_bar = tk.Entry(main_frame, font=("Arial", 12))
address_bar.bind("<Return>", go_to_website)
address_bar.pack(side="left", fill="both", expand=True)

# BT GO
button_go = tk.Button(main_frame, image=go_icon, command=go_to_website)
button_go.image = go_icon
button_go.pack(side="left")
#BT DOWNLOAD YOUTUBE
button_download = tk.Button(main_frame, image=download_icon)
button_download.image = download_icon
button_download.pack(side="left")
#BT FAVORITE
button_favorite = tk.Button(main_frame, image=favorite_icon, command=open_favorites)
button_favorite.image = favorite_icon
button_favorite.pack(side="left")
#BT DOWNLOAD MANAGER
button_downlist = tk.Button(main_frame, image=downlist_icon, command=show_downlist)
button_downlist.image = downlist_icon
button_downlist.pack(side="left")
#BT SETUP
button_settings = tk.Button(main_frame, image=settings_icon, command=show_settings)
button_settings.image = settings_icon
button_settings.pack(side="left")


page_frame = tk.Frame(root)
page_frame.pack(side="top", fill="both", expand=True)


# Criando a barra de status
status_bar = tk.Label(root, text="Carregado")
status_bar.pack(side="bottom", fill="x")

root.mainloop()