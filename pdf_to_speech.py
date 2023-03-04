#########################################################################################################################################################
#####################################  THIS PROGRAM WILL RENDER ALL OF THE .PDFs IN YOUR CURRENT DIRECTORY TO .MP3s  ####################################
#########################################################################################################################################################
                                #                                                                                                                       #
pdf_path = 'ENTER_PATH_HERE'    ###################################################### If there are no pdfs in your current directory, you can          # 
                                #                                                      specify a path here                                              #
start_page = 400                  ###################################################### Enter the page range you wish to render.                         #
                                #                                                                                                                       #
end_page = 407                    ###################################################### If you leave end_page equal to 0, then it renders all pages      #
                                #                                                                                                                       #
choose_bitrate = '320k'         ###################################################### Lessen the bitrate to create a smaller filesize. Less than 32k   #
                                #                                                      is not the best, more than 320 is unnecessary                    #
path_to_key = '/Users/remysteele/.config/gcloud/plucky-paratext-379015-abf653d0df1f.json'        ######################################################### Ender the key.json path                                       #
                                #                                                                                                                       #
smallest_font_size = 9        ###################################################### Remove text smaller than this size (footnotes, figure captions)  #
                                #                                                                                                                       #
largest_font_size = 17          ###################################################### Remove text smaller than this size (footnotes, figure captions)  #
                                #                                                                                                                       #
test_page = 0                   #########################################################################################################################
                                #                                                                                                                       #
test_text = True               #########################################################################################################################
                                #
x_tolerance = 0.8                   #########################################################################################################################
                                #                                                                                                                       #
y_tolerance = 6               #########################################################################################################################
                                #
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################























































import os, pydub, pdfplumber, glob, ntpath, sys, re
from send2trash import send2trash
from google.cloud import texttospeech_v1
from pydub import AudioSegment

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_to_key                                            
client = texttospeech_v1.TextToSpeechClient()
current_directory = str(os.getcwd())
filepaths = glob.glob("{}/*.pdf".format(current_directory))
filenames = []
voice = texttospeech_v1.VoiceSelectionParams (
    language_code = 'en-us',                                                # Select accent
    name = 'en-US-Neural2-G',                                               # Select the voice. The voices can be previewed on the Google text-to-speech API's website
    ssml_gender = texttospeech_v1.SsmlVoiceGender.FEMALE)
audio_config = texttospeech_v1.AudioConfig(
    audio_encoding = texttospeech_v1.AudioEncoding.LINEAR16)                 # Exports a WAV file to preserve quality

def convert(s):
    x = ""                                                                          # Function to concatinate a list of characters back to a string
    for y in s:
        x += y
    return x

def path_leaf(path):
    head, tail = ntpath.split(path)                                                 # A function that rips the filename from the path that works on all
    return tail or ntpath.basename(head)                                            # operating systems

def filter(page):
    filtered_page = page.filter(lambda obj: not \
                    (obj["object_type"] == "char" and obj["size"] < smallest_font_size))       # Filter out small characters
    filtered_page = filtered_page.filter(lambda obj: not \
                    (obj["object_type"] == "char" and obj["size"] > largest_font_size))
    return filtered_page

def show_image(page):
    im = page.to_image(resolution=100)
    im.draw_rects(page.extract_words(\
    x_tolerance=x_tolerance,y_tolerance = y_tolerance,keep_blank_chars=False))
    im.show()

if len(filepaths) == 0:
    filepaths = [pdf_path]                                                          # If there are no pdfs in the current directory, use pdf_path
    if filepaths[0].endswith('.pdf'):                                               # specified above to fetch filename
        filenames.append(path_leaf(filepaths[0]))
else:
    for file in os.listdir(current_directory):                                      # If there are multiple pdfs in the current directory, make a list
        if file.endswith('.pdf'):                                                   # of filenames to name output files
            filenames.append(file)

for p in range(len(filenames)):

    pdf_path = str(filepaths[p])
    output_filename = str(filenames[p]).replace('.pdf','')

    print('\n Starting render of {}\n'.format(output_filename))

    pdf = pdfplumber.open(pdf_path)

    if end_page == 0:
        pages = pdf.pages
    else:
        pages = pdf.pages[start_page-1:end_page-1]

    text = ""

    if test_page == 'ALL':
        for i in range(len(pages)):
            show_image(filter(pages[i]))
        cont = input("Continue? y/n \n")
        if cont != 'y':
            sys.exit("Try again!\n")
    elif isinstance(test_page, int):
        show_image(filter(pages[test_page]))
        cont = input("Continue? y/n \n")
        if cont != 'y':
            sys.exit("Try again!\n")
    elif isinstance(test_page, list):
        page_range = test_page[1]-test_page[0]
        for i in range(page_range):
            show_image(filter(pages[test_page[0]+i]))
        cont = input("Continue? y/n \n")
        if cont != 'y':
            sys.exit("Try again!\n")

    
    for i in range(len(pages)):

        filtered_page = pages[i].filter(lambda obj: not \
            (obj["object_type"] == "char" and obj["size"] < smallest_font_size))    # Filter out small characters
        filtered_page = filtered_page.filter(lambda obj: not \
            (obj["object_type"] == "char" and obj["size"] > largest_font_size))
        text = text + ' ' + filtered_page.extract_text(\
            x_tolerance=.8,y_tolerance = 3,keep_blank_chars=False)                  # These extraction parameters work pretty well
        pages[i].flush_cache()

    text =text.replace("^s", "").replace("^t", "").replace('•', ".").replace\
        ("\n", " ").replace("—", " ").replace("\r", " ").replace("'","").replace\
        ("\u0093", " ").replace("\u0094", "").replace("\u2019", "").replace\
        ("\u201c", " ").replace(":",".").replace('"',"").replace('&','').replace\
        ("'",'').replace('<','').replace('>','').replace(';',",").replace('- ',"")\
        .replace('[','').replace(']','').replace('-'," ")
    text = text.encode('ascii',"ignore").decode('unicode-escape')                   # Wash text of characters that wont be spoken

    regex = r"(?<=[A-Z][A-Z])[\s](?=[A-Z][a-z])|(?<=[a-z][a-z])[\s](?=[A-Z][A-Z])"
    subst = ". "
    text = re.sub(regex, subst, text, 0)

    characters = list(text)                                                         # Split text into a list characters

    b = re.findall(r".{0,4000}[.]", text)

    if test_text == True:
        print("\n",b, "\n")
        cont = input("Continue? y/n \n")
        if cont != 'y':
            sys.exit("Try again!\n")

    combined_sounds = AudioSegment.empty()

    print("\nRendering {} chuncks\n\n0 %".format(len(b)))

    for i in range(len(b)):                                                         # Loop through chunks, sending to google
        text = "<speech>" + b[i] + "</speech>"                                      # make the string ssml compatible

        synthesis_input = texttospeech_v1.SynthesisInput(ssml=text)

        response = client.synthesize_speech (                                       # Make Google do things
            input = synthesis_input,
            voice = voice,
            audio_config = audio_config
        )
        with open('text_to_speech_audio%.i.wav'%i,'wb',) as output:                 # Write the audio files in order as the loop goes round and round
                output.write(response.audio_content)

        sound = (AudioSegment.from_wav('text_to_speech_audio%.i.wav'%i))

        combined_sounds = combined_sounds+sound                                     # Create a list of the seperated audio files
        print("{} %".format(int(100*(i+1)/len(b))))

    combined_sounds.export("{}.mp3".format(output_filename),\
                            format="mp3", bitrate = choose_bitrate)                 # Concatinate and convert the audio files simultaneously

    for i in range(len(b)):                                                         # Delete the seperated audio files from harddrive

        os.remove('text_to_speech_audio%.i.wav'%i)

    cont = input('{} has been rendered. Trash PDF? y/n \n'.format(filenames[p]).replace('.pdf','.mp3'))
    if cont == 'y':
        send2trash(filepaths[p])