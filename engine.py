import pydub, pdfplumber



def proc_main(gsesh, output_filename, start_page, end_page, choose_bitrate, smallest_font_size, largest_font_size, test_pages, test_text, x_tolerance, y_tolerance):
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
