import curses, sys
from random import randint

class Block:
    S_BLANK = 0
    S_NUMBER = 1
    S_MARK = 2
    S_CLOSE = 3
    state = S_CLOSE
    mine = False
    number = 0

    def __init__(self, mine=False):
        self.mine = mine


class MineGame:
    MAX_VBLOCK_NUM = 9
    MAX_HBLOCK_NUM = 9
    DEF_VBLOCK_NUM = 9
    DEF_HBLOCK_NUM = 9
    DEF_MINE_NUM = 10
    """
        | ----------- BLOCK_WIDTH ----------- |
          |------HS_H------|  
                | --HF_H-- |

        ---------------------------------------
        |UL                                 UR|
        |                                     |
        |       #######################       |
        |       #######################       |
        |       #######################       |
        |       #######################       |
        |       #######################       |
        |                                     |
        |LL                                 LR|
        ---------------------------------------

        of course you can imagine vertical axis by yourself !
    """
    BLOCK_WIDTH = 7
    BLOCK_HEIGHT = 3
    BLOCK_HF_H = 1
    BLOCK_HF_V = 0
    BLOCK_HS_H = 3
    BLOCK_HS_V = 1
    ADD_LINE_NUM = 4
    D_UP = 1
    D_DOWN = 2
    D_LEFT = 3
    D_RIGHT = 4
    MINE_OFFSET = 15
    TITLE_STR = "Welcome to Mine Sweeping!"
    OPER1_STR = "[N]Start New Game   [X]Exit    [HJKL]Use 'hjkl' to move"
    OPER2_STR = "[M]Mark/Unmark   [O]Open Block   [I]Open All Surroundings"
    FAILURE_STR = "Boom!!! Game Over! Press <N> to start..."
    SUCCESS_STR = "Congratulations!! You Win!"


    def __init__(self, scr, width, height):
        self.scr = scr
        self.screenWidth = width
        self.screenHeight = height
        self.selX, self.selY = 1, 1
        self.blocks = [
            [
                Block() for j in range(0, MineGame.MAX_HBLOCK_NUM + 2)
            ] for i in range(0, MineGame.MAX_VBLOCK_NUM + 2)
        ]
        self.running = False


    def getCenterOfGrid(self, i, j):
        x = self.x0 + (i - 1) * (MineGame.BLOCK_WIDTH + 1)\
                + int((MineGame.BLOCK_WIDTH + 1) / 2)
        y = self.y0 + (j - 1) * (MineGame.BLOCK_HEIGHT + 1)\
                + int((MineGame.BLOCK_HEIGHT + 1) / 2)
        return x, y


    def initBackground(self, length, height, mine):
        self.vBlockNum = height
        self.hBlockNum = length
        self.mineNum = mine
        if self.vBlockNum > MineGame.MAX_VBLOCK_NUM\
                or self.hBlockNum > MineGame.MAX_HBLOCK_NUM:
            self.scr.addstr("cannot initialize, screen too small")
            self.scr.addstr(1, 0, "press any key to exit...")
            self.scr.getkey()
            return False
        self.width = (MineGame.BLOCK_WIDTH + 1) * self.hBlockNum + 1
        self.height = (MineGame.BLOCK_HEIGHT + 1) * self.vBlockNum + 1
        if self.screenWidth < self.width\
                or self.screenHeight < self.height + MineGame.ADD_LINE_NUM:
            self.scr.addstr("cannot initialize, screen too small")
            self.scr.addstr(1, 0, "press any key to exit...")
            self.scr.getkey()
            return False
        if mine < 1 or mine > self.vBlockNum * self.hBlockNum:
            self.scr.addstr("cannot initialize, invalid mine number")
            self.scr.addstr(1, 0, "press any key to exit...")
            self.scr.getkey()
            return False

        self.y0 = 2
        self.x0 = int((self.screenWidth - self.width) / 2)
        # title string
        self.scr.addstr(0,
                int((self.screenWidth - len(MineGame.TITLE_STR)) / 2),\
                MineGame.TITLE_STR, curses.A_BOLD)
        # horizontal lines
        for y in range(self.y0, self.y0 + self.height,
                MineGame.BLOCK_HEIGHT + 1):
            for x in range(self.x0 + 1, self.x0 + self.width - 1):
                self.scr.addch(y, x, curses.ACS_HLINE, curses.A_BOLD)
        # vertical lines
        for x in range(self.x0, self.x0 + self.width,
                MineGame.BLOCK_WIDTH + 1):
            for y in range(self.y0 + 1, self.y0 + self.height - 1):
                self.scr.addch(y, x, curses.ACS_VLINE, curses.A_BOLD)
        # grids
        for y in range(self.y0 + MineGame.BLOCK_HEIGHT + 1,\
                self.y0 + self.height - 1, MineGame.BLOCK_HEIGHT + 1):
            for x in range(self.x0 + MineGame.BLOCK_WIDTH + 1,\
                    self.x0 + self.width - 1, MineGame.BLOCK_WIDTH + 1):
                self.scr.addch(y, x, curses.ACS_PLUS, curses.A_BOLD)
        # borders
        for x in range(self.x0, self.x0 + self.width,
                MineGame.BLOCK_WIDTH + 1):
            self.scr.addch(self.y0, x, curses.ACS_TTEE, curses.A_BOLD)
            self.scr.addch(self.y0 + self.height - 1,\
                    x, curses.ACS_BTEE, curses.A_BOLD)
        for y in range(self.y0, self.y0 + self.height,
                MineGame.BLOCK_HEIGHT + 1):
            self.scr.addch(y, self.x0, curses.ACS_LTEE, curses.A_BOLD)
            self.scr.addch(y, self.x0 + self.width - 1,\
                    curses.ACS_RTEE, curses.A_BOLD)
        # corners
        self.scr.addch(self.y0, self.x0, curses.ACS_ULCORNER, curses.A_BOLD)
        self.scr.addch(self.y0, self.x0 + self.width - 1,\
                curses.ACS_URCORNER, curses.A_BOLD)
        self.scr.addch(self.y0 + self.height - 1, self.x0,\
                curses.ACS_LLCORNER, curses.A_BOLD)
        self.scr.addch(self.y0 + self.height - 1, self.x0 + self.width - 1,\
                curses.ACS_LRCORNER, curses.A_BOLD)
        # hint 1
        self.scr.addstr(self.y0 + self.height,\
                int((self.screenWidth - len(MineGame.OPER1_STR)) / 2),\
                MineGame.OPER1_STR, curses.A_BOLD)
        # hint 2
        self.scr.addstr(self.y0 + self.height + 1,\
                int((self.screenWidth - len(MineGame.OPER2_STR)) / 2),\
                MineGame.OPER2_STR, curses.A_BOLD)
        return True


    def fillBlockWithChAttr(self, _x, _y, ch, attr = None):
        for y in range(_y - MineGame.BLOCK_HF_V,
                _y + MineGame.BLOCK_HF_V + 1):
            for x in range(_x - MineGame.BLOCK_HF_H,
                    _x + MineGame.BLOCK_HF_H + 1):
                if attr is None:
                    self.scr.addch(y, x, ch)
                else:
                    self.scr.addch(y, x, ch, attr)


    def updateBlockStateUI(self, i, j):
        _x, _y = self.getCenterOfGrid(i, j)
        if self.blocks[i][j].state == Block.S_CLOSE:
            self.fillBlockWithChAttr(_x, _y, curses.ACS_BLOCK, curses.A_BOLD)
        elif self.blocks[i][j].state == Block.S_BLANK:
            self.fillBlockWithChAttr(_x, _y, ord(' '))
        elif self.blocks[i][j].state == Block.S_MARK:
            self.fillBlockWithChAttr(_x, _y, curses.ACS_DIAMOND)
        elif self.blocks[i][j].state == Block.S_NUMBER:
            self.fillBlockWithChAttr(_x, _y, ord(' '))
            self.scr.addstr(_y, _x,
                    str(self.blocks[i][j].number), curses.A_BOLD)


    def showSelect(self, show):
        x, y = self.getCenterOfGrid(self.selX, self.selY)
        if show:
            self.scr.addch(y - MineGame.BLOCK_HS_V,
                    x - MineGame.BLOCK_HS_H, curses.ACS_ULCORNER)
            self.scr.addch(y - MineGame.BLOCK_HS_V,
                    x + MineGame.BLOCK_HS_H, curses.ACS_URCORNER)
            self.scr.addch(y + MineGame.BLOCK_HS_V,
                    x - MineGame.BLOCK_HS_H, curses.ACS_LLCORNER)
            self.scr.addch(y + MineGame.BLOCK_HS_V,
                    x + MineGame.BLOCK_HS_H, curses.ACS_LRCORNER)
        else:
            self.scr.addch(y - MineGame.BLOCK_HS_V,
                    x - MineGame.BLOCK_HS_H, ord(' '))
            self.scr.addch(y - MineGame.BLOCK_HS_V,
                    x + MineGame.BLOCK_HS_H, ord(' '))
            self.scr.addch(y + MineGame.BLOCK_HS_V,
                    x - MineGame.BLOCK_HS_H, ord(' '))
            self.scr.addch(y + MineGame.BLOCK_HS_V,
                    x + MineGame.BLOCK_HS_H, ord(' '))


    def moveSelectBox(self, direction = 0):
        self.showSelect(False)
        if direction == MineGame.D_UP and self.selY > 1:
            self.selY -= 1
        elif direction == MineGame.D_DOWN and self.selY < self.vBlockNum:
            self.selY += 1
        elif direction == MineGame.D_LEFT and self.selX > 1:
            self.selX -= 1
        elif direction == MineGame.D_RIGHT and self.selX < self.hBlockNum:
            self.selX += 1
        elif direction == 0:
            self.selX, self.selY = 1, 1
        self.showSelect(True)


    def newGame(self):
        for j in range(1, self.vBlockNum + 1):
            for i in range(1, self.hBlockNum + 1):
                self.blocks[i][j].mine = False
                self.blocks[i][j].number = 0
                self.blocks[i][j].state = Block.S_CLOSE
                self.updateBlockStateUI(i, j)
        cur = 0
        while cur < self.mineNum:
            i, j = randint(1, self.hBlockNum), randint(1, self.vBlockNum)
            if self.blocks[i][j].mine == False:
                self.blocks[i][j].mine = True
                cur += 1
        for j in range(1, self.vBlockNum + 1):
            for i in range(1, self.hBlockNum + 1):
                if self.blocks[i - 1][j - 1].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i][j - 1].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i + 1][j - 1].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i - 1][j].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i + 1][j].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i - 1][j + 1].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i][j + 1].mine:
                    self.blocks[i][j].number += 1
                if self.blocks[i + 1][j + 1].mine:
                    self.blocks[i][j].number += 1
        self.mineLeft = self.mineNum
        self.scr.addstr(1, 0, " " * self.screenWidth)
        self.updateMineLeftUI()
        self.blockLeft = self.hBlockNum * self.vBlockNum
        self.moveSelectBox()
        self.running = True


    def updateMineLeftUI(self):
        self.scr.addstr(1, self.x0 + self.width - MineGame.MINE_OFFSET,
                "               ")
        if self.mineLeft > 0:
            self.scr.addstr(1, self.x0 + self.width - MineGame.MINE_OFFSET,
                    "Mine Left: {}".format(self.mineLeft), curses.A_BOLD)
        else:
            self.scr.addstr(1, self.x0 + self.width - MineGame.MINE_OFFSET,
                    "Mine Left: 0", curses.A_BOLD)


    def gameOver(self, win):
        self.scr.addstr(1, 0, " " * self.screenWidth)
        if win:
            self.scr.addstr(1, self.x0, MineGame.SUCCESS_STR, curses.A_BOLD)
        else:
            self.scr.addstr(1, self.x0, MineGame.FAILURE_STR, curses.A_BOLD)
        self.running = False


    def chainOpen(self, i, j):
        if i > 0 and i < self.hBlockNum + 1\
                and j > 0 and j < self.vBlockNum + 1\
                and self.blocks[i][j].state == Block.S_CLOSE\
                and self.blocks[i][j].mine == False:
            if self.blocks[i][j].number > 0:
                self.blocks[i][j].state = Block.S_NUMBER
                self.updateBlockStateUI(i, j)
                self.blockLeft -= 1
                if self.blockLeft == self.mineNum:
                    self.gameOver(True)
            else:
                self.blocks[i][j].state = Block.S_BLANK
                self.updateBlockStateUI(i, j)
                self.blockLeft -= 1
                if self.blockLeft == self.mineNum:
                    self.gameOver(True)
                self.chainOpen(i - 1, j - 1)
                self.chainOpen(i, j - 1)
                self.chainOpen(i + 1, j - 1)
                self.chainOpen(i - 1, j)
                self.chainOpen(i + 1, j)
                self.chainOpen(i - 1, j + 1)
                self.chainOpen(i, j + 1)
                self.chainOpen(i + 1, j + 1)


    def openCurrentBlock(self):
        if self.blocks[self.selX][self.selY].mine:
            self.gameOver(False)
        else:
            self.chainOpen(self.selX, self.selY)


    def checkSurroundingBlock(self, blocks, i, j):
        if self.blocks[i][j].state == Block.S_CLOSE:
            blocks.append((i, j))
        if self.blocks[i][j].state == Block.S_MARK:
            return 1
        else:
            return 0


    def openSurroundingBlock(self):
        if self.blocks[self.selX][self.selY].state == Block.S_NUMBER:
            surBlocks = []
            surMark = 0
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX - 1, self.selY - 1)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX, self.selY - 1)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX + 1, self.selY - 1)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX - 1, self.selY)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX + 1, self.selY)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX - 1, self.selY + 1)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX, self.selY + 1)
            surMark += self.checkSurroundingBlock(surBlocks,
                    self.selX + 1, self.selY + 1)
            if surMark == self.blocks[self.selX][self.selY].number:
                for t in surBlocks:
                    self.chainOpen(t[0], t[1])


    def handleInputChar(self, ch):
        if ch == ord('x') or ch == ord('X'):
            return False

        if ch == ord('n') or ch == ord('N'):
            self.newGame()
        elif self.running:
            if ch == ord('h') or ch == ord('H'):
                self.moveSelectBox(self.D_LEFT)
            elif ch == ord('j') or ch == ord('J'):
                self.moveSelectBox(self.D_DOWN)
            elif ch == ord('k') or ch == ord('K'):
                self.moveSelectBox(self.D_UP)
            elif ch == ord('l') or ch == ord('L'):
                self.moveSelectBox(self.D_RIGHT)
            elif ch == ord('m') or ch == ord('M'):
                if self.blocks[self.selX][self.selY].state == Block.S_CLOSE:
                    self.blocks[self.selX][self.selY].state = Block.S_MARK
                    self.mineLeft -= 1
                elif self.blocks[self.selX][self.selY].state == Block.S_MARK:
                    self.blocks[self.selX][self.selY].state = Block.S_CLOSE
                    self.mineLeft += 1
                self.updateMineLeftUI()
                self.updateBlockStateUI(self.selX, self.selY)
            elif ch == ord('o') or ch == ord('O'):
                if self.blocks[self.selX][self.selY].state == Block.S_CLOSE:
                    self.openCurrentBlock()
            elif ch == ord('i') or ch == ord('I'):
                self.openSurroundingBlock()
        return True


def go(stdscr, length, height, mine):
    curses.curs_set(False)

    gamer = MineGame(stdscr, curses.COLS, curses.LINES)
    if gamer.initBackground(length, height, mine) == False:
        return

    gamer.newGame()
    while gamer.handleInputChar(stdscr.getch()):
        pass


def main(args):
    if len(args) == 3:
        curses.wrapper(go, int(args[0]), int(args[1]), int(args[2]))
    elif len(args) == 0:
        curses.wrapper(go,
                MineGame.DEF_VBLOCK_NUM,
                MineGame.DEF_HBLOCK_NUM,
                MineGame.DEF_MINE_NUM)
    else:
        print("Enter 'length height mines' or nothing.")


if __name__ == "__main__":
    main(sys.argv[1:])

