# Builtin
import os, glob, ntpath, sys, re

# From req
import pydub, pdfplumber

from send2trash import send2trash
from google.cloud import texttospeech_v1
from pydub import AudioSegment
import G_class as G


#########################################################################################################################################################
#####################################  THIS PROGRAM WILL RENDER ALL OF THE .PDFs IN YOUR CURRENT DIRECTORY TO .MP3s  ####################################
#########################################################################################################################################################


# If there are no pdfs in your current directory, you can specify a path here
pdf_path = 'ENTER_PATH_HERE'

# Enter the page range you wish to render.
# If you leave start_page equal to 0, then it renders all pages
start_page = 0

# If you leave end_page equal to 0, then it renders only start_page
end_page = -1

# If False, then the MP3 filename will match the PDF filename, im manually setting this to false inside the loop cuz it sounds desireable unless this takes a string that can be a name???? 
output_filename = False

# Lessen the bitrate to create a smaller filesize. Less than 32k is not the best,
# more than 320 is unnecessary
choose_bitrate = '320k'

# Remove text smaller than this size (footnotes, figure captions)
smallest_font_size = 8.5

# Remove text larger than this size
largest_font_size = 30

# If the required libraries are installed,
# True will open a temporary image so you can verify the PDF scrape before rendering
test_pages = False

# If True, then the text to be rendered will be displayed so you can verify before rendering
test_text = False

# how wide the characters can be apart before they start rendering as seperate words
x_tolerance = 0.8

# How far the lines can be above or below
y_tolerance = 3


gsesh = G.Gsession()

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

if len(gsesh.filepaths) == 0:
    gsesh.filepaths = [pdf_path]                                                          # If there are no pdfs in the current directory, use pdf_path
    if gsesh.filepaths[0].endswith('.pdf'):                                               # specified above to fetch filename
        gsesh.filenames.append(path_leaf(gsesh.filepaths[0]))
else:
    for file in os.listdir(gsesh.current_directory):                                      # If there are multiple pdfs in the current directory, make a list
        if file.endswith('.pdf'):                                                   # of filenames to name output files
            gsesh.filenames.append(file)

for p in range(len(gsesh.filenames)):

    pdf_path = str(gsesh.filepaths[p])
    if output_filename == False:
        output_filename = str(gsesh.filenames[p]).replace('.pdf','')

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

    print("\nRendering {} chuncks\n\n0 %".format(len(b)))
    gsesh.render(b, output_filename, choose_bitrate, p)
