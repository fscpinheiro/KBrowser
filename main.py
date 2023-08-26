from pytube import YouTube
import os
from moviepy.editor import *

def downloadYoutube(link, path):
    print("url to download: "+link)
    print("url to save: "+path)

    urltosave = os.path.normpath(path)
    print("url fixed to save: "+urltosave)

    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    if not os.path.exists(urltosave):
        print("diretorio criado")
        os.makedirs(urltosave)
    try:
        print("salvando...")
        videofile = youtubeObject.download(urltosave)
        video_name = os.path.basename(videofile)
        som_name, extensao = os.path.splitext(video_name)
        print("SOM name: "+som_name)
        som_name = som_name+".mp3"
        print("Update som_name: "+som_name)
        dir_name = os.path.dirname(videofile)
        print("Video Name: "+video_name)
        print("Convertendo....")
        arquivomp4 = os.path.join(dir_name, video_name)
        arquivomp3 = os.path.join(dir_name, som_name)
        print(arquivomp4)
        MP4ToMP3(arquivomp4, arquivomp3)
    except:
        print("Ocorreu um erro")
    print("Download concluido")

def MP4ToMP3(mp4, mp3):
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()


linkdown = input("Informe o link do video para download: ")
linksave = input("Onde deseja salvar: ")

downloadYoutube(linkdown, linksave)

