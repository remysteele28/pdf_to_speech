import os, pydub, pdfplumber
from google.cloud import texttospeech_v1
from pydub import AudioSegment

if os.path.isfile(./tospeech.txt):
    with open("./tospeech.txt","r") as f:
        tospeech = f.read()
else:
\
\
pdf_path = '/Users/remysteele/Documents/UMASS/UMASS SPRING 2023/ANTHRO 103/MISC/Explorations-An-Open-Invitation-To-Biological-Anthropology-Shook, Nelson.pdf'



start_page = 274
end_page = 305

choose_bitrate = '320k'                                                                 # Lessen the bitrate to create a smaller filesize. Less than 32k is not the best

desired_output_filename = ''                                                        # Enter an output filename

path_to_key = '/Users/remysteele/.config/gcloud/plucky-paratext-379015-abf653d0df1f.json'

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

text = text.replace("^s", " ").replace("^t", "    ").replace('•', ".").replace("\n", " ")

text = text.replace("U+0093", " ").replace("U+0094", "    ")

characters = list(text)                                                                   # Split text into a list characters

size_limit=4950

def convert(s):                                                                         # Function to concatinate a list of characters
 
    # initialization of empty string 
    new = ""
 
    # traverse in the string
    for x in s:
        new += x
 
    # return string
    return new

def split_text():
    char_groups = []

    k = 0

    loops = int(len(characters)/size_limit)

    current_group = ""

    remaining_chars = len(characters)

    for i in range(loops):
        for j in range(size_limit):
            current_group = current_group + characters[k]
            k += 1
        current_list = list(current_group)
        while current_list[-1] != ' ':
            current_list.pop()
            k -= 1
        current_list.pop()
        k -= 1
        char_groups = char_groups + [convert(current_list)]
        remaining_chars = remaining_chars - len(convert(current_list))
        current_group = ""


    for i in range(remaining_chars):
        current_group = current_group + characters[k]
        k += 1
    char_groups = char_groups + [current_group]
    return char_groups

b = split_text()

for i in range(int(len(characters)/size_limit)+1):                                      # Loop through the first 4500 characters, then the next 4500...

        text = "<speak>"+b[i]+"</speak>"                                                   # make the string ssml compatible

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

for i in range(int(len(characters)/size_limit)+1):                                      # Delete the seperated audio files from harddrive

        os.remove('text_to_speech_audio%.i.wav'%i)