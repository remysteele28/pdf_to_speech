pdf_path = '/Users/remysteele/Documents/UMASS/UMASS SPRING 2023/ANTHRO 103/MISC/Explorations-An-Open-Invitation-To-Biological-Anthropology-Shook, Nelson.pdf'

start_page = 274
end_page = 305

choose_bitrate = '320k'                                                                 # Lessen the bitrate to create a smaller filesize. Less than 32k is not the best

desired_output_filename = 'ANTHRO 103 - CH 8'                                         # Enter an output filename

path_to_key = '/Users/remysteele/.config/gcloud/plucky-paratext-379015-abf653d0df1f.json'

import os, pydub, pdfplumber
from google.cloud import texttospeech_v1
from pydub import AudioSegment

pdf = pdfplumber.open(pdf_path)

pages = pdf.pages[start_page+6:end_page+7]

text = ""

for i in range(len(pages)):

    filtered_page = pages[i].filter(lambda obj: not (obj["object_type"] == "char" and obj["size"] < 9))
    text = text + ' ' + filtered_page.extract_text(x_tolerance=1,keep_blank_chars=False)
    pages[i].flush_cache()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_to_key                                            
client = texttospeech_v1.TextToSpeechClient()
combined_sounds = AudioSegment.empty()


text = text[20:]

char_limit = 4500                                                                       # Google only allows each request to be 5000 bytes > about 5 minutes of audio

def convert(s):                                                                         # Function to concatinate a list of characters
 
    # initialization of empty string 
    new = ""
 
    # traverse in the string
    for x in s:
        new += x
 
    # return string
    return new

text = text.replace("^s", " ").replace("^t", "    ").replace('•', " ")

text = text.replace("U+0093", " ").replace("U+0094", "    ")

characters = list(text)                                                            # Split text into a list characters

for i in range(int(len(characters)/char_limit)+2):                                      # Loop through the first 4500 characters, then the next 4500...

        b = convert(characters[(char_limit*i-10*i):(char_limit+char_limit*i-10*i)])     # Convert the first 4500 characters in the list back into a string. Then, convert the next 4500 characters,
                                                                                        # with a small 10 character buffer so that the word is guarenteed to be understood
        text = "<speak>"+b+"</speak>"                                                   # make the string ssml compatible

        synthesis_input = texttospeech_v1.SynthesisInput(ssml=text)

        voice = texttospeech_v1.VoiceSelectionParams (
                language_code = 'en-us',                                                # Select accent
                name = 'en-US-Neural2-G',                                               # Select the voice. The voices can be previewed on the Google text-to-speech API's website
                ssml_gender = texttospeech_v1.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech_v1.AudioConfig(
                audio_encoding = texttospeech_v1.AudioEncoding.LINEAR16                 # Exports a WAV file to preserve quality
        )
        response = client.synthesize_speech (                                           # Make Google do things
                input = synthesis_input,
                voice = voice,
                audio_config = audio_config
        )
        with open('text_to_speech_audio%.i.wav'%i,'wb',) as output:                     # Write the audio files in order as the loop goes round and round
                output.write(response.audio_content)

        sound = (AudioSegment.from_wav('text_to_speech_audio%.i.wav'%i))

        combined_sounds = combined_sounds+sound                                         # Create a list of the seperated audio files

combined_sounds.export("{}.mp3".format(desired_output_filename),\
                        format="mp3", bitrate = choose_bitrate)                         # Concatinate and convert the audio files simultaneously

for i in range(int(len(characters)/char_limit)+2):                                      # Delete the seperated audio files from harddrive

        os.remove('text_to_speech_audio%.i.wav'%i)