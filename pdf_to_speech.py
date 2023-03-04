# Builtin
import os, glob, ntpath, sys, re

# From req
import pydub, pdfplumber

from send2trash import send2trash
from google.cloud import texttospeech_v1
from pydub import AudioSegment
import G_class as G
from multiprocessing import Process
from engine import *
from display import *
import curses

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


if __name__ == '__main__':
    #               GUI
    # Start the engine in the background as a processes
    pz = Process(target=proc_main(gsesh, output_filename, start_page, end_page, choose_bitrate, smallest_font_size, largest_font_size, test_pages, test_text, x_tolerance, y_tolerance))
    pz.start()

    # Start the curses GUI
    curses.wrapper(display)


