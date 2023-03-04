import curses

def display(stdscr):
    stdscr.clear()
    stdscr.timeout(500)

    maxy, maxx = stdscr.getmaxyx()
    curses.newwin(2, maxx, 3, 1)

    # invisible cursor
    curses.curs_set(0)

    if (curses.has_colors()):
        # Start colors in curses
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
    stdscr.refresh()

    curses.init_pair(1, 0, -1)
    curses.init_pair(2, 1, -1)
    curses.init_pair(3, 2, -1)
    curses.init_pair(4, 3, -1)

    bottomBox = curses.newwin(0, maxx - 2, maxy - 38, 1)
    bottomBox.box()
    bottomBox.addstr("Craig Finder Console")
    bottomBox.refresh()
    bottomwindow = curses.newwin(35, maxx - 4, maxy - 37, 2)
    bottomwindow.addstr("START\n", curses.A_UNDERLINE)
    bottomwindow.refresh()

    with open("app_header/money-ne") as file_object:
        head = file_object.readlines()
    for line in head:
        stdscr.addstr("{:20s}".format(line), curses.color_pair(4))
    stdscr.refresh()

    while True:
        with open("conpsuedole/out", "r+") as out:
            lines = out.readlines()
            out.write('')
        for line in lines:
            bottomwindow.addstr(line)
            bottomwindow.insertln()
        bottomwindow.scrollok(True)
        bottomwindow.scroll(-1)
        bottomwindow.refresh()
        bottomwindow.clear()
        event = stdscr.getch()
        if event == ord("q"):
            break
