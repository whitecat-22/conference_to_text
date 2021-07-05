from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import ffmpeg
import os

# wav形式に変換
stream = ffmpeg.input("audio_only.m4a")
stream = ffmpeg.output(stream, 'zoom_rec.wav')
ffmpeg.run(stream)

API_KEY = os.environ.get("API_KEY")
URL = os.environ.get("URL")

# APIキー入力
authenticator = IAMAuthenticator(
    API_KEY
)
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url(
    URL
)

# APIから受け取った文字起こし結果をファイル出力


class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        with open('proceedings.txt', mode='a') as f:
            f.write(data['results'][1]['alternatives'][0]
                    ['transcript'].replace(' ', '') + '\n')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))


myRecognizeCallback = MyRecognizeCallback()

# wav変換したファイルを開いてAPIを呼び出し
with open('zoom_rec.wav',
          'rb') as audio_file:
    audio_source = AudioSource(audio_file)
    response = speech_to_text.recognize_using_websocket(
        audio=audio_source,
        content_type='audio/wav',
        recognize_callback=myRecognizeCallback,
        model='ja-JP_BroadbandModel',
        keywords=['colorado'],
        keywords_threshold=0.5)

# 出力したファイルを読み込んで結果表示
with open('proceedings.txt') as f:
    result_logs = f.readlines()
    last_result_log = result_logs[-1].replace('\n', '')
    print(last_result_log.replace(' ', ''))
