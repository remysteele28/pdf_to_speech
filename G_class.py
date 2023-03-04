import json
from send2trash import send2trash
from google.cloud import texttospeech_v1
import os, glob
from pydub import AudioSegment

class Gsession:

    def __init__(self):
        # Credentials
        print("Session initialization")
        path_to_key = glob.glob(r'*.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_to_key[0]
        self.path_to_key = path_to_key
        self.client = texttospeech_v1.TextToSpeechClient()
        
        #directory and files
        self.current_directory = str(os.getcwd())
        self.filepaths = glob.glob("{}/*.pdf".format(self.current_directory))
        self.filenames = []

        #params
        self.voice = texttospeech_v1.VoiceSelectionParams (
            language_code = 'en-us',                                                # Select accent
            name = 'en-US-Neural2-G',                                               # Select the voice. The voices can be previewed on the Google text-to-speech API's website
            ssml_gender = texttospeech_v1.SsmlVoiceGender.FEMALE)
        self.audio_config = texttospeech_v1.AudioConfig(
            audio_encoding = texttospeech_v1.AudioEncoding.LINEAR16)

    def render(self, b, filename, bitrate, p):
        combined_sounds = AudioSegment.empty()
        for i in range(len(b)):                                                         # Loop through chunks, sending to google individually
            text = "<speech>" + b[i] + "</speech>"                                      # make the string ssml compatible

            synthesis_input = texttospeech_v1.SynthesisInput(ssml=text)

            response = self.client.synthesize_speech (                                       # Make Google do things
                input = synthesis_input,
                voice = self.voice,
                audio_config = self.audio_config
            )
            with open('text_to_speech_audio%.i.wav'%i,'wb',) as output:                 # Write the audio files in order as the loop goes round and round
                    output.write(response.audio_content)

            sound = (AudioSegment.from_wav('text_to_speech_audio%.i.wav'%i))

            combined_sounds = combined_sounds+sound                                     # Create a list of the seperated audio files
            print("{} %".format(int(100*(i+1)/len(b))))

        combined_sounds.export("{}.mp3".format("./" + filename),\
            format="mp3", bitrate = bitrate)                                     # Concatinate and convert the audio files simultaneously

        for i in range(len(b)):                                                         # Delete the seperated audio files from harddrive
            os.remove('text_to_speech_audio%.i.wav'%i)

        cont = input('{} has been rendered. Trash PDF? y/n \n'.format(self.filenames[p])\
            .replace('.pdf','.mp3'))                                                    # Ask if user wants to trash PDF after rendering
        if cont == 'y':
            send2trash(filepaths[p])
