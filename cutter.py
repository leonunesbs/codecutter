import ffmpeg
import os
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo


class Cutter:
    def __init__(self, url):

        self.set_url(url)
        self.menu()

    def set_url(self, url: str):
        self.url = url
        self.yt = YouTube(url)
        return url

    def get_stream_data(self):
        files = os.listdir('./')
        if ['audio.mp4', 'video.mp4'] not in files:
            print('INICIANDO COLETA DE ÁUDIO/VÍDEO')
            yt_video = self.yt.streams.filter(
                only_video=True, subtype='mp4').order_by('resolution').desc().first()
            yt_audio = self.yt.streams.filter(
                only_audio=True, subtype='mp4').first()

            def show_progress_bar(stream, chunk, bytes_remaining):
                video_progress = (yt_video.filesize -
                                  bytes_remaining) / yt_video.filesize * 100
                audio_progress = (yt_audio.filesize -
                                  bytes_remaining) / yt_audio.filesize * 100

                progress = ((yt_video.filesize + yt_audio._filesize) -
                            bytes_remaining) / (yt_video.filesize + yt_audio._filesize) * 100

                if video_progress < 0:
                    video_progress = 0
                if audio_progress < 0:
                    audio_progress = 0

                mean = (video_progress + audio_progress) / 2

                print('[', '=' * int(mean), f'{mean:.1f}%]')

            self.yt.register_on_progress_callback(show_progress_bar)

            yt_video.download(filename='video')
            yt_audio.download(filename='audio')

    def merge_audio_video(self):
        input_video = ffmpeg.input('video.mp4')
        input_audio = ffmpeg.input('audio.mp4')

        ffmpeg.output(input_video, input_audio,
                      f'{"".join(filter(str.isalpha, self.yt.title))}.mp4').run()

        os.remove('video.mp4')
        os.remove('audio.mp4')

        return self.menu()

    def make_clip(self, title, start, end):
        ffmpeg_extract_subclip(f'{"".join(filter(str.isalpha, self.yt.title))}.mp4', start,
                               end, targetname='clip.mp4')
        os.rename('clip.mp4', f'{title}.mp4')

        return self.menu()

    def upload(self):
        # loggin into the channel
        channel = Channel()
        channel.login("client_secret.json", "credentials.txt")

        # setting up the video that is going to be uploaded
        video = LocalVideo(file_path="teste.mp4")

        # setting snippet
        título = str(input('Título: '))
        video.set_title(título)
        descrição = str(input('Descrição: '))
        video.set_description(descrição)
        video.set_tags(["this", "tag"])
        video.set_category('entertainment')
        video.set_default_language("pt-BR")

        # setting status
        video.set_embeddable(True)
        video.set_license("creativeCommon")
        video.set_privacy_status("private")
        video.set_public_stats_viewable(True)
        video.set_made_for_kids(False)

        # setting thumbnail
        # video.set_thumbnail_path('test_thumb.png')

        # uploading video and printing the results
        video = channel.upload_video(video)
        print(video.id)
        print(video)

        # liking video
        video.like()

    def menu(self):
        print('====MENU====')
        print(self.yt.title)
        print(
            f'1. Baixar vídeo')
        print('2. Novo clipe')
        print('3. Setar URL')
        print('4. Upar')
        print('5. Resetar')
        option = str(input('Digite uma opção: '))

        def process_option(option):
            def baixar_video():
                self.get_stream_data()
                self.merge_audio_video()

            def novo_clip():
                print('Novo clipe de: ', self.yt.title)
                start = int(input('Início em segundos: '))
                end = int(input('Fim em segundos: '))
                title = str(input('Título: '))
                self.make_clip(title, start, end)

            def nova_url():
                url = str(input('Nova URL: '))
                while not url:
                    f = open("ultima_url.txt", "r")
                    url = f.read()
                    if not url:
                        url = str(input('Insira a URL do video no YouTube: '))
                self.set_url(url)
                self.menu()

            def reset():
                files = os.listdir('./')
                for file in files:
                    if file not in ['cutter.py', '1x', 'requirements.txt', 'env', '.vscode', 'ultima_url.txt', 'client_secret.json', 'src']:
                        os.remove(file)
                nova_url()

            if option == '1':
                baixar_video()
            elif option == '2':
                novo_clip()
            elif option == '3':
                nova_url()
            elif option == '4':
                self.upload()
            elif option == '5':
                reset()

        process_option(option)


url = str(input('Insira a URL do video no YouTube: '))
while not url:
    f = open("ultima_url.txt", "r")
    url = f.read()
    f.close()
    if not url:
        url = str(input('Insira a URL do video no YouTube: '))

f = open("ultima_url.txt", "w")
f.write(url)
f.close()


cutter = Cutter(url)
# cutter.get_stream_data()
# cutter.merge_audio_video()
# cutter.make_clip(10, 50)
