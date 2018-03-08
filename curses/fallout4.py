import curses
import json
import os
import time

class Pipboy:
    """
    ----------------- terminal border (no width, invisible) -----------------
    |                          <borderMargin=1>                             |
    |  +----------------------- Pip-Boy border --------------------------+  |
    |  |                         title line 1                            |  |
    |  |                         title line 2                            |  |
    |  |                       blank title line                          |  |
    |  |==========================separator==============================|  |
    |  |                      <contentMargin=1>                          |  |
    |  |    *********************************************************    |  |
    |  |    *                                                       *    |  |
    |  |    *                    content area                       *    |  |
    |  |    *                                                       *    |  |
    |  |    *                                                       *    |  |
    |2 | 4  *                                                       *  4 | 2|
    |  |    *                                                       *    |  |
    |  |    *                                                       *    |  |
    |  |    *                                                       *    |  |
    |  |    *********************************************************    |  |
    |  |                       <contentMargin=0>                         |  |
    |  |                        terminal line                            |  |
    |  +----------------------- Pip-Boy border --------------------------+  |
    |                           <borderMargin=1>                            |
    |                             menu line 1                               |
    |                             menu line 2                               |
    |                           blank menu line                             |
    ----------------- terminal border (no width, invisible) -----------------

    terminal size: w0 x h0
    Pip-Boy size: w1 x h1
    content area size: w2 x h2
    """

    def __init__(self, scr):
        # TODO: turn off debug
        self.debug = True
        self.version = "1.1.0"

        # top, bottom, left, right
        self.borderMargin = [ 1, 1, 2, 2 ]
        self.contentMargin = [ 1, 1, 1, 1 ]
        self.menuKeyLineCount = 2
        self.titleLineCount = 2

        # intra separator, inter separator
        self.menuKeySeparator = [ ") ", "    " ]
        self.defaultMenuKey = [ ("WASD", "Navigate"), ("E", "Select"), ("Tab", "Exit") ]

        # data related
        self.dataFileName = "fallout4consumable.json"
        self.lastSelect = -1

        # initialize
        self.stdscr = scr
        self.stdscr.bkgdset(' ', curses.color_pair(1))
        self.examineScreenSize()

        # create sub window and show background
        self.showBackground()
        h = self.h0 - (self.borderMargin[0] + 1 + self.titleLineCount + 2 + self.contentMargin[0]) - (1 + self.menuKeyLineCount + self.borderMargin[1] + 2 + self.contentMargin[1])
        w = self.w0 - (self.borderMargin[2] + 1 + self.contentMargin[2]) - (self.borderMargin[3] + 1 + self.contentMargin[3])
        self.scr = self.stdscr.subwin(h, w, self.borderMargin[0] + 1 + self.titleLineCount + 2 + self.contentMargin[0], self.borderMargin[2] + 1 + self.contentMargin[2])
        self.h2, self.w2 = self.scr.getmaxyx()

        # create rolling pad, 64 lines is almost enough for all item...
        self.pad = curses.newpad(64, self.w2)
        self.pad.bkgdset(' ', curses.color_pair(1))

    def showFatalError(self, errorMsg):
        err1 = errorMsg
        err2 = "Press any key to exit..."
        if self.w0 < len(err1) or self.w0 < len(err2) or self.h0 < 2:
            # WTF!!
            exit()

        self.stdscr.clear()
        self.stdscr.addstr(int((self.h0 - 1) / 2), int((self.w0 - len(err1)) / 2), err1)
        self.stdscr.addstr(int((self.h0 - 1) / 2) + 1, int((self.w0 - len(err2)) / 2), err2)
        self.stdscr.refresh()
        self.stdscr.getkey()
        exit()

    def examineScreenSize(self):
        """ examine screen size and we get (w0, h0) """
        self.h0, self.w0 = self.stdscr.getmaxyx()
        if self.w0 < 80 or self.h0 < 24:
            self.showFatalError("Screen too small for Pip-Boy!")

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
        y = self.fancyShowText("Fallout 4 Consumable Browser", 0, 0)
        y = self.fancyShowText("Browse and edit wasteland consumables. You can even add your own items here!", y, 0)
        y = y + 1
        selections = [
                ("Browse Consumables", self.handleBrowsePage),
                ("Edit New Consumable", self.handleNewPage),
                ("[ Make A Query! ]", self.handleQueryPage)]
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
            winEnd = min(len(entries), self.h2)

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
                    self.viewItemPageFather = self.handleBrowsePage
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
                    winEnd = winEnd + 1
                    self.browsePageShowEntry(entries, select, winBegin, winEnd)
            else:
                pass

        return handler

    def browsePageShowEntry(self, entries, select, begin, end):
        self.scr.clear()
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

        # prepare data
        e = []
        for item in self.data:
            e.append(item["name"].lower())

        cache = []
        cache.append(("", e))

        select = 0
        winBegin, winEnd = 0, min(len(e), self.h2)

        # show page
        queryKey1 = [ ("Arrow Key", "Navigate"), ("Enter", "Select"), ("Tab", "Exit") ]
        queryKey2 = [ ("[A-Za-z']", "Enter item name") ]
        self.showMenu(queryKey1, queryKey2)
        self.browsePageShowEntry(e, select, winBegin, winEnd)

        # handle key
        while (1):
            c = self.stdscr.getch()
            if (c > 64 and c < 91) or (c > 96 and c < 123) or (c == 39) or (c == 32):
                if c > 64 and c < 91:
                    c -= 32
                query = cache[-1][0] + chr(c)
                entries = []
                for e in cache[-1][1]:
                    if query in e:
                        entries.append(e)
                cache.append((query, entries))

                select = 0
                winBegin, winEnd = 0, min(len(cache[-1][1]), self.h2)
                self.queryPageShowEntry(cache[-1][0], cache[-1][1], select, winBegin, winEnd)
                self.showFakeTerminal(cache[-1][0])
            elif c == 263:
                if len(cache) > 1:
                    cache = cache[:-1]
                    select = 0
                    winBegin, winEnd = 0, min(len(cache[-1][1]), self.h2)
                    self.queryPageShowEntry(cache[-1][0], cache[-1][1], select, winBegin, winEnd)
                    self.showFakeTerminal(cache[-1][0])
            elif c == 259:
                if select > winBegin:
                    select -= 1
                    self.queryPageShowEntry(cache[-1][0], cache[-1][1], select, winBegin, winEnd)
                elif select > 0:
                    select -= 1
                    winBegin -= 1
                    winEnd -= 1
                    self.queryPageShowEntry(cache[-1][0], cache[-1][1], select, winBegin, winEnd)
            elif c == 258:
                if select < winEnd - 1:
                    select += 1
                    self.queryPageShowEntry(cache[-1][0], cache[-1][1], select, winBegin, winEnd)
                elif select < len(cache[-1][1]) - 1:
                    select += 1
                    winBegin += 1
                    winEnd += 1
                    self.queryPageShowEntry(cache[-1][0], cache[-1][1], select, winBegin, winEnd)
            elif c == 9:
                handler = self.handleMenuPage
                self.showFakeTerminal()
                self.showMenu(self.defaultMenuKey)
                self.lastSelect = -1
                break
            elif c == 10:
                for i in range(len(cache[0][1])):
                    if cache[0][1][i] == cache[-1][1][select]:
                        self.lastSelect = i
                        break
                handler = self.handleViewItemPage
                self.viewItemPageFather = self.handleQueryPage
                self.showFakeTerminal()
                self.showMenu(self.defaultMenuKey)
                break
            else:
                self.showDebugInfo(str(c))

        return handler

    def queryPageShowEntry(self, query, entries, select, begin, end):
        self.scr.clear()
        for i in range(end - begin):
            entry = entries[begin + i]
            index = entry.find(query)
            if i + begin == select:
                self.scr.addstr(i, 0, entry[0:index], curses.A_REVERSE)
                self.scr.addstr(i, index, query, curses.A_REVERSE | curses.A_BOLD)
                self.scr.addstr(i, index + len(query), entry[index+len(query):len(entry)], curses.A_REVERSE)
            else:
                self.scr.addstr(i, 0, entry[0:index])
                self.scr.addstr(i, index, query, curses.A_BOLD)
                self.scr.addstr(i, index + len(query), entry[index+len(query):len(entry)])
        self.scr.refresh()

    def handleViewItemPage(self):
        handler = None

        dataLength = self.viewItemPageFillData(self.data[self.lastSelect])
        pos = 0
        padX = self.borderMargin[2] + 1 + self.contentMargin[2]
        padY = self.borderMargin[0] + 1 + self.titleLineCount + 2 + self.contentMargin[0]
        self.pad.refresh(pos, 0, padY, padX, padY + self.h2 - 1, padX + self.w2 - 1)

        while (1):
            c = self.stdscr.getch()
            if c == 9 or c == 69 or c == 101:
                handler = self.viewItemPageFather
                break
            elif c == 87 or c == 119:
                if pos > 0:
                    pos -= 1
                    self.pad.refresh(pos, 0, padY, padX, padY + self.h2 - 1, padX + self.w2 - 1)
            elif c == 83 or c == 115:
                if pos + self.h2 < dataLength:
                    pos += 1
                    self.pad.refresh(pos, 0, padY, padX, padY + self.h2 - 1, padX + self.w2 - 1)
            else:
                pass

        return handler

    def viewItemPageFillData(self, data):
        self.pad.clear()
        y = 0
        coef3 = [ 0.05, 0.35, 0.65 ]
        coef2 = [ 0.05, 0.50 ]

        # name
        self.pad.addstr(y, 0, data["name"], curses.A_BOLD)
        # add-on
        if "add-on" in data:
            self.pad.addstr(y, len(data["name"]) + 2, "[" + data["add-on"] + "]")
        # type
        self.pad.addstr(y, self.w2 - len(data["type"]), data["type"])
        y = y + 1

        # weight
        self.pad.addstr(y, int(self.w2 * coef3[0]), "Weight: " + str(data["weight"]))
        # value
        self.pad.addstr(y, int(self.w2 * coef3[1]), "Value: " + str(data["value"]))
        # baseid
        self.pad.addstr(y, int(self.w2 * coef3[2]), "Base ID: " + str(data["baseid"]))
        y = y + 2

        # effect
        self.pad.addstr(y, 0, "Effect", curses.A_BOLD)
        y = y + 1
        if "inst-effect" in data:
            i = 0
            for e in data["inst-effect"]:
                self.pad.addstr(y, int(self.w2 * coef2[i % len(coef2)]), "+{} {}".format(data["inst-effect"][e], e))
                i = i + 1
                if i % 2 == 0:
                    y = y + 1
            if i % 2 == 1:
                y = y + 1
        if "cont-effect" in data:
            for e in data["cont-effect"]:
                if "effect" in e:
                    self.pad.addstr(y, int(self.w2 * coef2[0]), "{} for {}s".format(e["effect"], e["second"]))
                else:
                    eName, eValue = "", ""
                    for e0 in e:
                        if e0 != "second":
                            eName = e0
                            eValue = e[e0]
                    self.pad.addstr(y, int(self.w2 * coef2[0]), "+{} {} for {}s".format(eValue, eName, e["second"]))
                y = y + 1

        # crafting
        if "crafting" in data:
            y = y + 1
            self.pad.addstr(y, 0, "Crafting", curses.A_BOLD)
            crafting = data["crafting"]
            if "XP" in crafting:
                self.pad.addstr(y, 10, "+ " + str(crafting["XP"]) + " XP")
            self.pad.addstr(y, self.w2 - len(crafting["requirements"]), crafting["requirements"], curses.A_UNDERLINE)
            s = self.buildCraftingString(data["name"], crafting)
            y = y + 1
            self.pad.addstr(y, int(self.w2 * coef3[0]), s)
            y = y + 1 + int(len(s) / self.w2)

        # as a component
        # TODO: navigate from here
        if "component-of" in data:
            y += 1
            self.pad.addstr(y, 0, "Component Of", curses.A_BOLD)
            y = y + 1
            for comp in data["component-of"]:
                self.pad.addstr(y, int(self.w2 * coef2[0]), comp)
                y = y + 1

        return y

    def buildCraftingString(self, name, crafting):
        s = name + "(" + str(crafting["produces"]) + "):   "
        comp = []
        for material in crafting["materials"]:
            comp.append(material + "(" + str(crafting["materials"][material]) + ")")
        s = s + " + ".join(comp)
        return s

    def showBackground(self):
        """ wipe out current screen and show default background """
        self.stdscr.clear()
        self.showMenu(self.defaultMenuKey)
        self.showBorder()
        self.showTitle()
        self.showFakeTerminal()
        self.stdscr.refresh()

    def showBorder(self):
        """ after this method, we get (w1, h1) """
        xBegin = self.borderMargin[2]
        xEnd = self.w0 - 1 - self.borderMargin[3]
        yBegin = self.borderMargin[0]
        yEnd = self.h0 - 1 - 1 - self.menuKeyLineCount - self.borderMargin[1]
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

    def getMenuKeyLength(self, keys):
        length = 0
        for (key, intro) in keys:
            length += len(key) + len(self.menuKeySeparator[0]) + len(intro)
        length += (len(keys) - 1) * len(self.menuKeySeparator[1])
        return length

    def showMenuKeyMiddleAlign(self, keys, y):
        keyLength = self.getMenuKeyLength(keys)
        if self.w0 < keyLength:
            self.showFatalError("DEBUG: too many menu keys in one line!!")
        x = int((self.w0 - keyLength) / 2)
        for (key, intro) in keys:
            self.stdscr.addstr(y, x, key + self.menuKeySeparator[0] + intro + self.menuKeySeparator[1], curses.A_BOLD)
            x += len(key) + len(self.menuKeySeparator[0]) + len(intro) + len(self.menuKeySeparator[1])

    def showMenu(self, keyLine1 = None, keyLine2 = None):
        self.stdscr.addstr(self.h0 - 1 - self.menuKeyLineCount, 0, " " * self.w0)
        self.stdscr.addstr(self.h0 - 1 - self.menuKeyLineCount + 1, 0, " " * self.w0)
        if keyLine1 is not None:
            self.showMenuKeyMiddleAlign(keyLine1, self.h0 - 1 - self.menuKeyLineCount)
        if keyLine2 is not None:
            self.showMenuKeyMiddleAlign(keyLine2, self.h0 - 1 - self.menuKeyLineCount + 1)

    def showTitle(self):
        title = "RobCo Personal Information Processor (Version " + self.version + ")"
        author = "Powered by Joseph"
        length = self.w0 - (self.borderMargin[2] + 1) - (self.borderMargin[3] + 1)
        x1 = self.borderMargin[2] + 1 + int((length - len(title)) / 2)
        x2 = self.borderMargin[2] + 1 + int((length - len(author)) / 2)
        y = self.borderMargin[0] + 1
        self.stdscr.addstr(y, x1, title)
        self.stdscr.addstr(y + 1, x2, author)
        self.stdscr.addstr(y + self.titleLineCount + 1, self.borderMargin[2] + 1, "=" * length, curses.A_BOLD)

    def showFakeTerminal(self, text = ""):
        x = self.borderMargin[2] + 1
        y = self.h0 - 1 - self.menuKeyLineCount - self.borderMargin[1] - 1 - 1
        length = self.w1 - 2
        self.stdscr.addstr(y, x, " " * length)
        self.stdscr.addstr(y, x, " > ", curses.A_BOLD)
        self.stdscr.addstr(y, x + 3, text + "_")

    def showDebugInfo(self, s):
        if self.debug:
            self.stdscr.addstr(self.h0 - 1, 0, ' ' * (self.w0 - 1), curses.color_pair(2))
            self.stdscr.addstr(self.h0 - 1, 0, s, curses.color_pair(2))

def resizeToStandard(stdscr):
    h, w = stdscr.getmaxyx()
    if h < 24 or w < 80:
        print("\x1b[8;24;80t")
        stdscr.getkey()

def main(stdscr):
    resizeToStandard(stdscr)

    # initialize environment
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    # start Pip-Boy
    pi = Pipboy(stdscr)
    pi.start()

if __name__ == "__main__":
    curses.wrapper(main)
