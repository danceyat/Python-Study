import curses

class Pipboy:
    MENU_LINES = 3

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
        self.scr = self.stdscr.subwin(self.h0 - self.MENU_LINES, self.w0, 0, 0)
        self.showBackground()

    def start(self):
        pass

    def showBackground(self):
        self.stdscr.clear()
        self.scr.border()
        self.showMenu()

    def showMenu(self):
        menuKey = [ ( "WASD", "Navigate" ), ( "E", "Select" ), ( "Tab", "Cancel" ) ]
        menuKeyLength = 0
        for ( k, v ) in menuKey:
            # add 1 blank for ' ', 2 blanks for '[' and ']'
            menuKeyLength += len(k) + len(v) + 1 + 2
        # add 3 blanks between every tuple
        menuKeyLength += (len(menuKey) - 1) * 3
        # TODO: make sure terminal width is bigger than menuKeyLength
        x = int((self.w0 - menuKeyLength) / 2)
        y = self.h0 - self.MENU_LINES
        #self.stdscr.addstr(y, x, menu1)
        for ( k, v ) in menuKey:
            self.stdscr.addch(y, x, '[')
            x += 1
            self.stdscr.addstr(y, x, k, curses.A_BOLD)
            x += len(k)
            self.stdscr.addstr(y, x, "] ")
            x += 2
            self.stdscr.addstr(y, x, v)
            x += len(v)
            self.stdscr.addstr(y, x, "   ")
            x += 3

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

    # TODO: remove this
    stdscr.getkey()

if __name__ == "__main__":
    curses.wrapper(main)
