#########################################################################################################################################################
#####################################  THIS PROGRAM WILL RENDER ALL OF THE .PDFs IN YOUR CURRENT DIRECTORY TO .MP3s  ####################################
#########################################################################################################################################################
                                #                                                                                                                       #
pdf_path = 'ENTER_PATH_HERE'    #################################################### If there are no pdfs in your current directory, you can specify    #
                                #                                                    a path here                                                        #
start_page = 0                  #################################################### Enter the page range you wish to render.                           #
                                #                                                    If you leave start_page equal to 0, then it renders all pages      #
end_page = 0                    #################################################### If you leave end_page equal to 0, then it renders only start_page  #
                                #                                                                                                                       #
output_filename = False         #################################################### If False, then the MP3 filename will match the PDF filename        #
                                #                                                                                                                       #
choose_bitrate = '320k'         #################################################### Lessen the bitrate to create a smaller filesize. Less than 32k     #
                                #                                                    is not the best, more than 320 is unnecessary                      #
path_to_key = 'REDACTED'        #################################################### Ender the key.json path                                            #
                                #                                                                                                                       #
smallest_font_size = 8.5        #################################################### Remove text smaller than this size (footnotes, figure captions)    #
                                #                                                                                                                       #
largest_font_size = 30          #################################################### Remove text larger than this size                                  #
                                #                                                                                                                       #
test_pages = False              #################################################### If the required libraries are installed, True will open a          #
                                #                                                    temporary image so you can verify the PDF scrape before rendering  #
test_text = False               #################################################### If True, then the text to be rendered will be displayed so you     #
                                #                                                    can verify before rendering                                        #
x_tolerance = 0.8               #################################################### how wide the characters can be apart before they start rendering   #
                                #                                                    as seperate words                                                  #
y_tolerance = 3                 #################################################### How far the lines can be above or below                            #
                                #                                                                                                                       #
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

def path_leaf(path):
    head, tail = ntpath.split(path)                                                 # A function that rips the filename from the path that works on all
    return tail or ntpath.basename(head)                                            # operating systems
def filter(page):
    filtered_page = page.filter(lambda obj: not \
                    (obj["object_type"] == "char" and \
                     obj["size"] < smallest_font_size))                             # Filter out small characters
    filtered_page = filtered_page.filter(lambda obj: not \
                    (obj["object_type"] == "char" and \
                     obj["size"] > largest_font_size))                              # Filter out large characters
    return filtered_page
def show_image(page):
    im = page.to_image(resolution=100)                                              # If the required libraries are installed, this will output a preview
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
    if output_filename == False:
        output_filename = str(filenames[p]).replace('.pdf','')

    print('\n Starting render of {}\n'.format(output_filename))

    pdf = pdfplumber.open(pdf_path)

    if start_page == 0:
        pages = pdf.pages                                                           # Render all pages
    elif end_page == 0:
        end_page = start_page+1                                                     # Render one page
        pages = pdf.pages[start_page-1:end_page-1]
    else:
        pages = pdf.pages[start_page-1:end_page-1]                                  # Render page range

    text = ""

    if test_pages == True:
        for i in range(len(pages)):
            show_image(filter(pages[i]))                                            # Create test pages
        cont = input("Continue? y/n \n")
        if cont != 'y':
            sys.exit("Try again!\n")

    char_size = []

    for i in range(len(pages)):
        k = 0
        filtered_page = pages[i].filter(lambda obj: not \
            (obj["object_type"] == "char" and obj["size"] < smallest_font_size))    # Filter out small characters
        filtered_page = filtered_page.filter(lambda obj: not \
            (obj["object_type"] == "char" and obj["size"] > largest_font_size))
        text = text + ' ' + filtered_page.extract_text(\
            x_tolerance=x_tolerance,y_tolerance = y_tolerance,\
            keep_blank_chars=False)                                                 # These extraction parameters work pretty well
        # for j in range(30):                                                       # Cant figure out how to add a period (voice break) after text above
        #     if text[j] == ' ':                                                    # a certain fontsize switches back to normal sized text
        #         k += 1                                                            # (after reading a title, take a short break before reading the first)
        #         char_size.append(filtered_page.chars[j-k]['size'])                # sentence of the section)
        #     char_size.append(filtered_page.chars[j-k]['size'])
        #     if char_size[j] > 13 and char_size[j+1] < 10:
        #         text = text[:j] + '..............' + text[j:]
        #     print(filtered_page.chars[j-k]['size'],filtered_page.chars[j-k]['text'],text[j])
        pages[i].flush_cache()

    text = text.replace("^s", "").replace("^t", "").replace('•', ".").replace\
        ("\n", " ").replace("—", " ").replace("\r", " ").replace("'","").replace\
        ("\u0093", " ").replace("\u0094", "").replace("\u2019", "").replace\
        ("\u201c", " ").replace(":",".").replace('"',"").replace('&','').replace\
        ("'",'').replace('<','').replace('>','').replace(';',",").replace\
        ('- ',"").replace('[','').replace(']','').replace('-'," ")
    text = text.encode('ascii',"ignore").decode('unicode-escape')                   # Wash text of characters that wont be spoken

    regex = r"(?<=[A-Z][A-Z])[\s](?=[A-Z][a-z])|(?<=[a-z][a-z])[\s](?=[A-Z][A-Z])"  # Add period (voice break) after text in all capitals (section title)
    subst = ". "                                                                    # changes back to normal text
    text = re.sub(regex, subst, text, 0)

    b = re.findall(r".{0,4000}[.]", text)                                           # Split text into chunks

    if test_text == True:
        print("\n",b, "\n")                                                         # Check text before rendering
        cont = input("Continue? y/n \n")
        if cont != 'y':
            sys.exit("Try again!\n")

    combined_sounds = AudioSegment.empty()

    print("\nRendering {} chuncks\n\n0 %".format(len(b)))

    for i in range(len(b)):                                                         # Loop through chunks, sending to google individually
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
        format="mp3", bitrate = choose_bitrate)                                     # Concatinate and convert the audio files simultaneously

    for i in range(len(b)):                                                         # Delete the seperated audio files from harddrive
        os.remove('text_to_speech_audio%.i.wav'%i)

    cont = input('{} has been rendered. Trash PDF? y/n \n'.format(filenames[p])\
        .replace('.pdf','.mp3'))                                                    # Ask if user wants to trash PDF after rendering
    if cont == 'y':
        send2trash(filepaths[p])