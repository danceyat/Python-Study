import curses
import json
import os
import time

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
        self.init = False
        # TODO: turn off debug
        self.debug = True
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
            self.stdscr.getkey()
            return

        # create sub window and show background
        self.stdscr.bkgdset(' ', curses.color_pair(1))
        self.showBackground()
        h = self.h0 - (self.marginTop + 1 + self.paddingTop + self.titleLineCount) - (self.paddingBottom + 1 + self.marginBottom + self.menuLineCount)
        w = self.w0 - (self.marginLeft + 1 + self.paddingLeft) - (self.marginRight + 1 + self.paddingRight)
        self.scr = self.stdscr.subwin(h, w, self.marginTop + 1 + self.paddingTop + self.titleLineCount, self.marginLeft + 1 + self.paddingLeft)
        self.h2, self.w2 = self.scr.getmaxyx()
        #self.scr.border()

        self.dataFileName = "fallout4consumable.json"
        self.lastSelect = -1
        self.init = True

    def start(self):
        self.holotapeLoaded = False

        handlePage = self.handleLoadingPage
        while (handlePage):
            handlePage = handlePage()

        if self.holotapeLoaded:
            self.storeData()

    def handleLoadingPage(self):
        handler = None

        # show page
        self.scr.clear()
        self.scr.addstr(self.h2 - 1, 0, " > ", curses.A_BOLD)
        if self.holotapeLoaded:
            self.scr.addstr(0, 0, "[ Holotape(WASTELAND CONSUMABLE) ]", curses.A_REVERSE)
        else:
            self.scr.addstr(0, 0, "[ Load Holotape ]", curses.A_REVERSE)
        self.scr.refresh()

        # handle key
        while (1):
            c = self.stdscr.getch()
            if c == 69 or c == 101:
                if not self.holotapeLoaded:
                    self.scr.addstr(self.h2 - 1, 0, " > Loading...", curses.A_BOLD)
                    self.scr.refresh()
                    self.loadData()
                    self.holotapeLoaded = True
                handler = self.handleMenuPage
                break
            elif c == 9:
                handler = None
                break
            else:
                pass

        return handler

    def loadData(self):
        self.parseError = False
        try:
            with open(self.dataFileName, 'r') as json_data:
                self.data = json.load(json_data)
        except FileNotFoundError:
            self.showDebugInfo("File not found.")
            self.data = []
        except json.JSONDecodeError:
            self.parseError = True
            self.showDebugInfo("JSON decode error.")
            self.data = []

    def storeData(self):
        if self.parseError:
            os.rename(self.dataFileName, self.dataFileName + ".bak")

        with open(self.dataFileName, 'w') as dataFile:
            json.dump(self.data, dataFile, indent = 4, sort_keys = True)

    def handleMenuPage(self):
        handler = None

        # show page
        self.scr.clear()
        self.scr.addstr(self.h2 - 1, 0, " > ", curses.A_BOLD)
        y = self.fancyShowText("Fallout 4 Consumable Browser", 0, 0)
        y = self.fancyShowText("Browse and edit wasteland consumables. You can even add your own items here!", y, 0)
        y = y + 1
        selections = [
                ( "Browse Consumables", self.handleBrowsePage),
                ( "Edit New Consumable", self.handleNewPage),
                ( "[ Make A Query! ]", self.handleQueryPage)]
        select = 0
        self.menuPageShowMenu(selections, select, y)
        self.scr.refresh()

        # handle key
        while (1):
            c = self.stdscr.getch()
            if c == 69 or c == 101:
                handler = selections[select][1]
                break
            elif c == 9:
                handler = self.handleLoadingPage
                break
            elif c == 87 or c == 119:
                if select > 0:
                    select = select - 1
                    self.menuPageShowMenu(selections, select, y)
                    self.scr.refresh()
            elif c == 83 or c == 115:
                if select < len(selections) - 1:
                    select = select + 1
                    self.menuPageShowMenu(selections, select, y)
                    self.scr.refresh()
            else:
                pass

        return handler

    def menuPageShowMenu(self, selections, select, y0):
        for i in range(len(selections)):
            if i == select:
                self.scr.addstr(y0 + i, 0, selections[i][0], curses.A_REVERSE)
            else:
                self.scr.addstr(y0 + i, 0, selections[i][0])

    def fancyShowText(self, s, y0, x0):
        # TODO: check input parameters?
        i = 0
        x, y = x0, y0
        self.stdscr.nodelay(1)
        while (1):
            if not len(s) > i:
                break

            c = self.stdscr.getch()
            if c != -1:
                self.scr.addstr(y, x, s[i:])
                l = len(s) - i
                if l > self.w2 - x:
                    l = l - (self.w2 - x)
                    y = y + 1 + 1 + int(l / self.w2)
                else:
                    y = y + 1
                # set x to 0 to get the right y
                x = 0
                # show all remaining text
                break

            self.scr.addch(y, x, s[i])
            self.scr.refresh()
            x = x + 1
            if x >= self.w2:
                x = 0
                y = y + 1
                if y >= self.h2:
                    # no enough room for text
                    break
            i = i + 1
            time.sleep(0.02)

        self.stdscr.nodelay(0)
        # return next empty line
        if x == 0:
            return y
        else:
            return y + 1

    def handleBrowsePage(self):
        handler = None

        # prepare data
        entries = []
        for item in self.data:
            entries.append(item["name"])

        if self.lastSelect > 0:
            select = self.lastSelect
            winBegin = self.lastWinBegin
            winEnd = self.lastWinEnd
        else:
            select = 0
            winBegin = 0
            winEnd = min(len(entries), self.h2 - 2)

        # show page
        self.browsePageShowEntry(entries, select, winBegin, winEnd)

        # handle key
        while (1):
            c = self.stdscr.getch()
            if c == 69 or c == 101:
                if select < len(entries):
                    self.lastSelect = select
                    self.lastWinBegin = winBegin
                    self.lastWinEnd = winEnd
                    handler = self.handleViewItemPage
                    break
            elif c == 9:
                self.lastSelect = -1
                handler = self.handleMenuPage
                break
            elif c == 87 or c == 119:
                if select > winBegin:
                    select = select - 1
                    self.browsePageShowEntry(entries, select, winBegin, winEnd)
                elif select > 0:
                    select = select - 1
                    winBegin = winBegin - 1
                    winEnd = winEnd - 1
                    self.browsePageShowEntry(entries, select, winBegin, winEnd)
            elif c == 83 or c == 115:
                if select < winEnd - 1:
                    select = select + 1
                    self.browsePageShowEntry(entries, select, winBegin, winEnd)
                elif select < len(entries) - 1:
                    select = select + 1
                    winBegin = winBegin + 1
                    winEnd = winEnd  + 1
                    self.browsePageShowEntry(entries, select, winBegin, winEnd)
            else:
                pass

        return handler

    def browsePageShowEntry(self, entries, select, begin, end):
        self.scr.clear()
        self.scr.addstr(self.h2 - 1, 0, " > ", curses.A_BOLD)
        for i in range(end - begin):
            if i + begin == select:
                self.scr.addstr(i, 0, entries[begin + i], curses.A_REVERSE)
            else:
                self.scr.addstr(i, 0, entries[begin + i])
        self.scr.refresh()

    def handleNewPage(self):
        handler = None

        return handler

    def handleQueryPage(self):
        handler = None

        return handler

    def handleViewItemPage(self):
        handler = None

        # show page
        data = self.data[self.lastSelect]
        select = 0
        self.viewItemPageShowData(data, select)

        # handle key
        while (1):
            c = self.stdscr.getch()
            if c == 69 or c == 101:
                handler = None
                break
            elif c == 9:
                handler = self.handleBrowsePage
                break
            else:
                pass

        return handler

    def viewItemPageShowData(self, data, select):
        # TODO: consider situation of line overflow
        self.scr.clear()
        self.scr.addstr(self.h2 - 1, 0, " > ", curses.A_BOLD)
        y = 0
        coef3 = [ 0.05, 0.35, 0.65 ]
        coef2 = [ 0.05, 0.50 ]

        # name
        self.scr.addstr(y, 0, data["name"], curses.A_BOLD)
        # add-on
        if "add-on" in data:
            self.scr.addstr(y, len(data["name"]) + 2, "[" + data["add-on"] + "]")
        # type
        self.scr.addstr(y, self.w2 - len(data["type"]), data["type"])
        y = y + 1

        # weight
        self.scr.addstr(y, int(self.w2 * coef3[0]), "Weight: " + str(data["weight"]))
        # value
        self.scr.addstr(y, int(self.w2 * coef3[1]), "Value: " + str(data["value"]))
        # baseid
        self.scr.addstr(y, int(self.w2 * coef3[2]), "Base ID: " + str(data["baseid"]))
        y = y + 2

        # effect
        self.scr.addstr(y, 0, "Effect", curses.A_BOLD)
        y = y + 1
        if "inst-effect" in data:
            i = 0
            for e in data["inst-effect"]:
                self.scr.addstr(y, int(self.w2 * coef2[i % len(coef2)]), "+{} {}".format(data["inst-effect"][e], e))
                i = i + 1
                if i % 2 == 0:
                    y = y + 1
            if i % 2 == 1:
                y = y + 1
        if "cont-effect" in data:
            for e in data["cont-effect"]:
                if "effect" in e:
                    self.scr.addstr(y, int(self.w2 * coef2[0]), "{} for {}s".format(e["effect"], e["second"]))
                else:
                    eName, eValue = "", ""
                    for e0 in e:
                        if e0 != "second":
                            eName = e0
                            eValue = e[e0]
                    self.scr.addstr(y, int(self.w2 * coef2[0]), "+{} {} for {}s".format(eValue, eName, e["second"]))
                y = y + 1
        y = y + 1

        # crafting
        if "crafting" in data:
            self.scr.addstr(y, 0, "Crafting", curses.A_BOLD)
            crafting = data["crafting"]
            if "XP" in crafting:
                self.scr.addstr(y, 10, "+ " + str(crafting["XP"]) + " XP")
            self.scr.addstr(y, self.w2 - len(crafting["requirements"]), crafting["requirements"], curses.A_UNDERLINE)
            s = self.buildCraftingString(data["name"], crafting)
            y = y + 1
            self.scr.addstr(y, int(self.w2 * coef3[0]), s)
            y = y + 2 + int(len(s) / self.w2)

        # as one component
        # TODO: navigate from here
        # TODO: too much line
        if "component-of" in data:
            self.scr.addstr(y, 0, "Component Of", curses.A_BOLD)
            y = y + 1
            for comp in data["component-of"]:
                self.scr.addstr(y, int(self.w2 * coef2[0]), comp)
                y = y + 1
        self.scr.refresh()

    def buildCraftingString(self, name, crafting):
        s = name + "(" + str(crafting["produces"]) + "):   "
        comp = []
        for material in crafting["materials"]:
            comp.append(material + "(" + str(crafting["materials"][material]) + ")")
        s = s + " + ".join(comp)
        return s

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
        title = "RobCo Personal Information Processor (Version 1.0.0)"
        author = "Powered by Joseph"
        length = self.w0 - (self.marginLeft + 1 + self.paddingLeft) - (self.marginRight + 1 + self.paddingRight)
        x1 = self.marginLeft + 1 + self.paddingLeft + int((length - len(title)) / 2)
        x2 = self.marginLeft + 1 + self.paddingLeft + int((length - len(author)) / 2)
        y = self.marginTop + 1 + self.paddingTop
        self.stdscr.addstr(y, x1, title)
        self.stdscr.addstr(y + 1, x2, author)
        self.stdscr.addstr(y + self.titleLineCount - 1, self.marginLeft + 1 + self.paddingLeft, "-" * length, curses.A_BOLD)

    def showDebugInfo(self, s):
        if self.debug:
            self.stdscr.addstr(self.h0 - 1, 0, ' ' * (self.w0 - 1), curses.color_pair(2))
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
    if pi.init:
        pi.start()

if __name__ == "__main__":
    curses.wrapper(main)
