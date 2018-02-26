import curses

class Pipboy:
    menuLineCount = 3
    menuKeyIntraSeparator = ") "
    menuKeyInterSeparator = "    "
    titleLineCount = 4
    marginTop = 1
    marginBottom = 1
    marginLeft = 2
    marginRight = 2
    paddingTop = 1
    paddingBottom = 0
    paddingLeft = 1
    paddingRight = 1

    """
    +---------------- terminal border (no width, invisible)
    |           1
    |2 +------------- Pip-Boy border
    |  |        2
    |  |
    |  |      xxxxx   title line
    |  |       xxx
    |  |
    |  |4   ********* content area
    |  |    *
    |  |    *

    ......

    |  |    *
    |  |    *
    |  |    *********
    |  |        2
    |  |
    |  +------------- Pip-Boy border
    |           1
    |        xxxxxxx  menu line
    |
    |
    +---------------- terminal border (no width, invisible)

    terminal size: w0 x h0
    Pip-Boy size: w1 x h1
    content area size: w2 x h2
    """

    def __init__(self, scr):
        self.stdscr = scr

        # show error message and exit if terminal's too small
        self.h0, self.w0 = self.stdscr.getmaxyx()
        if self.w0 < 80 or self.h0 < 24:
            err1 = "Screen too small for Pip-Boy!"
            err2 = "Press any key to exit..."
            if self.w0 < len(err1) or self.h0 < 2:
                # WTF!!
                return
            self.stdscr.addstr(int((self.h0 - 1) / 2), int((self.w0 - len(err1)) / 2), err1)
            self.stdscr.addstr(int((self.h0 - 1) / 2) + 1, int((self.w0 - len(err2)) / 2), err2)
            return

        # create sub window and show background
        self.stdscr.bkgdset(' ', curses.color_pair(1))
        self.showBackground()
        h = self.h0 - (self.marginTop + 1 + self.paddingTop + self.titleLineCount) - (self.paddingBottom + 1 + self.marginBottom + self.menuLineCount)
        w = self.w0 - (self.marginLeft + 1 + self.paddingLeft) - (self.marginRight + 1 + self.paddingRight)
        self.scr = self.stdscr.subwin(h, w, self.marginTop + 1 + self.paddingTop + self.titleLineCount, self.marginLeft + 1 + self.paddingLeft)
        self.h2, self.w2 = self.scr.getmaxyx()
        #self.scr.border()

    def start(self):
        state = "initial"
        selection = ""
        holotapeLoaded = False
        while (1):
            # show content
            if state == "initial":
                self.scr.clear()
                self.scr.addstr(self.h2 - 1, 0, " > ", curses.A_BOLD)
                if not holotapeLoaded:
                    self.showSelected(0, 0, "[ Load Holotape ]")
                else:
                    self.showSelected(0, 0, "[ Holotape (Fallout4Consumables) ]")
                self.scr.addstr(1, 0, "[ Save Holotape ]")

            # handle input
            c = self.stdscr.getch()
            if c == 69 or c == 101:
                pass
            elif c == 9:
                break
            else:
                self.showDebugInfo(str(c))

    def showSelected(self, y, x, s):
        self.scr.addstr(y, x, s + ' ' * (self.w2 - len(s)), curses.A_REVERSE)

    def showBackground(self):
        self.stdscr.clear()
        self.showBorder()
        self.showMenu()
        self.showTitle()

    def showBorder(self):
        xBegin = self.marginLeft
        xEnd = self.w0 - 1 - self.marginRight
        yBegin = self.marginTop
        yEnd = self.h0 - 1 - self.menuLineCount - self.marginBottom
        self.stdscr.addch(yBegin, xBegin, '+', curses.A_BOLD)
        self.stdscr.addch(yBegin, xEnd, '+', curses.A_BOLD)
        self.stdscr.addch(yEnd, xBegin, '+', curses.A_BOLD)
        self.stdscr.addch(yEnd, xEnd, '+', curses.A_BOLD)
        for _x in range(xBegin + 1, xEnd):
            self.stdscr.addch(yBegin, _x, '-', curses.A_BOLD)
            self.stdscr.addch(yEnd, _x, '-', curses.A_BOLD)
        for _y in range(yBegin + 1, yEnd):
            self.stdscr.addch(_y, xBegin, '|', curses.A_BOLD)
            self.stdscr.addch(_y, xEnd, '|', curses.A_BOLD)
        self.w1 = xEnd - xBegin + 1
        self.h1 = yEnd - yBegin + 1

    def showMenu(self):
        menuKey = [ ( "WASD", "Navigate" ), ( "E", "OK" ), ( "Tab", "Cancel" ) ]
        menuKeyLength = 0
        for ( k, v ) in menuKey:
            menuKeyLength += len(k) + len(self.menuKeyIntraSeparator) + len(v)
        menuKeyLength += (len(menuKey) - 1) * len(self.menuKeyInterSeparator)
        # TODO: make sure terminal width is bigger than menuKeyLength
        x = int((self.w0 - menuKeyLength) / 2)
        y = self.h0 - self.menuLineCount
        #self.stdscr.addstr(y, x, menu1)
        for ( k, v ) in menuKey:
            self.stdscr.addstr(y, x, k + self.menuKeyIntraSeparator + v + self.menuKeyInterSeparator, curses.A_BOLD)
            x += len(k) + len(self.menuKeyIntraSeparator) + len(v) + len(self.menuKeyInterSeparator)

    def showTitle(self):
        title = "Wasteland Consumable Manual (Version 1.0.0)"
        author = "Powered by Joseph"
        length = self.w0 - (self.marginLeft + 1 + self.paddingLeft) - (self.marginRight + 1 + self.paddingRight)
        x1 = self.marginLeft + 1 + self.paddingLeft + int((length - len(title)) / 2)
        x2 = self.marginLeft + 1 + self.paddingLeft + int((length - len(author)) / 2)
        y = self.marginTop + 1 + self.paddingTop
        self.stdscr.addstr(y, x1, title)
        self.stdscr.addstr(y + 1, x2, author)
        self.stdscr.addstr(y + self.titleLineCount - 1, self.marginLeft + 1 + self.paddingLeft, "-" * length, curses.A_BOLD)

    def showDebugInfo(self, s):
        self.stdscr.addstr(self.h0 - 1, 0, s, curses.color_pair(2))

def resizeToStandard(stdscr):
    print("\x1b[8;24;80t")
    stdscr.getkey()

def main(stdscr):
    #resizeToStandard(stdscr)

    # initialize environment
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    # start Pip-Boy
    pi = Pipboy(stdscr)
    # TODO: may add parameters here
    pi.start()

if __name__ == "__main__":
    curses.wrapper(main)
