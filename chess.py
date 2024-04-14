import pygame, os
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

PATH = os.path.dirname(__file__)+'/'
FPS = 60
SCREEN_W = 700
SCREEN_H = 700
screen = pygame.display.set_mode((SCREEN_W,SCREEN_H))
pygame.display.set_caption("Chess")
HOR = ('a','b','c','d','e','f','g','h')
VER = tuple([i for i in range(8,0,-1)])

class Board:
    def __init__(self, size, pos):
        self.size = size
        self.pos = pos
        self.border = pygame.rect.Rect(*pos,*[size]*2)
        self.board = {}

        self.create()

    def create(self):
        x,y = self.pos
        box_size = self.size//8
        colors = ((245, 204, 160),(101, 69, 31))
        colors = ((203,207,174),(89,123,54))
        n=0
        for i in range(8):
            n=1-n
            for j in range(8):
                n=1-n
                box = pygame.rect.Rect(x+i*box_size,y+j*box_size,*[box_size]*2)
                self.board[(HOR[i],VER[j])] = (box,colors[n])
    
    def revolve(self):
        for key in self.board:
            value = self.board[key]
            value[0].right = self.size+self.pos[0]*2-value[0].x
            value[0].bottom = self.size+self.pos[1]*2-value[0].y

    def display(self):
        pygame.draw.rect(screen, (100,100,100), self.border,1,5)
        for x in self.board:
            pygame.draw.rect(screen,self.board[x][1],self.board[x][0])
            border = pygame.Rect(0,0,*[self.size//8]*2)
            border.center = self.board[x][0].center
            # pygame.draw.rect(screen, (100,60,50), border, 1)


class Moves:
    def __init__(self):
        self.castling = [1,1]
        self.moves = []

    def rook(self,hor,ver):
        spaces=[[],[],[],[]]
        for i in HOR[HOR.index(hor)+1:]:
            if hor<'h':
                spaces[0].append((i,ver))
        for i in HOR[HOR.index(hor)-1::-1]:
            if hor>'a':
                spaces[1].append((i,ver))
        for i in VER[VER.index(ver)+1:]:
            if ver>1:
                spaces[2].append((hor,i))
        for i in VER[VER.index(ver)-1::-1]:
            if ver<8:
                spaces[3].append((hor,i))
        return spaces
    
    def knight(self,hor,ver):
        spaces = []
        if hor>'b':
            x = HOR[HOR.index(hor)-2]
            if ver>1:
                spaces.append((x,ver-1))
            if ver<8:
                spaces.append((x,ver+1))
        if hor<'g':
            x = HOR[HOR.index(hor)+2]
            if ver>1:
                spaces.append((x,ver-1))
            if ver<8:
                spaces.append((x,ver+1))
        if ver>2:
            x = HOR.index(hor)
            y = VER[VER.index(ver)+2]
            if hor>'a':
                spaces.append((HOR[x-1],y))
            if hor<'h':
                spaces.append((HOR[x+1],y))
        if ver<7:
            x = HOR.index(hor)
            y = VER[VER.index(ver)-2]
            if hor>'a':
                spaces.append((HOR[x-1],y))
            if hor<'h':
                spaces.append((HOR[x+1],y))
        return spaces
    
    def bishop(self,hor,ver):
        spaces=[[],[],[],[]]
        i=0
        for x in (HOR[HOR.index(hor)+1:],HOR[HOR.index(hor)-1::-1]):
            for y in (VER[VER.index(ver)+1:],VER[VER.index(ver)-1::-1]):
                n = min(len(x),len(y))
                if ((x==HOR[HOR.index(hor)+1:] and hor<'h') or (x==HOR[HOR.index(hor)-1::-1] and hor>'a')) and ((y==VER[VER.index(ver)+1:] and ver>1) or (y==VER[VER.index(ver)-1::-1] and ver<8)):
                    for j in range(n):
                        spaces[i].append((x[j],y[j]))
                i+=1
        return spaces

    def king(self,hor:str,ver:int,player:dict,white:dict):
        spaces = []
        special = []
        side = []
        x = HOR.index(hor)
        def repeat(t):
            if ver>1:
                spaces.append((t,ver-1))
            if ver<8:
                spaces.append((t,ver+1))
        if hor>'a':
            spaces.append((HOR[x-1],ver))
            repeat(HOR[x-1])
        if hor<'h':
            spaces.append((HOR[x+1],ver))
            repeat(HOR[x+1])
        repeat(hor)

        def repeat2(ver):
            for x in player:
                if player[x][1]==ver:
                    if player[x][0] in ('b','c','d'):
                        break
            else:
                special.extend([(i,ver) for i in ('a','b','c')])
                side.append('a')
            for x in player:
                if player[x][1]==ver:
                    if player[x][0] in ('f','g'):
                        break
            else:
                special.extend([(i,ver) for i in ('g','h')])
                side.append('h')
            

        if player==white and self.castling[0]:
            repeat2(1)
        elif self.castling[1]:
            repeat2(8)
        return spaces, special, side
    
    def pawns(self,hor:str,ver:int,player:dict,opponent:dict,white:dict):
        x = HOR.index(hor)
        def repeat(i, bonus=None):
            available,captures,enpassant=[],[],[]
            if ver<8 and ver>1:
                move = (hor,ver+i)
                if move not in player.values() and move not in opponent.values():
                    available.append(move)
                    if bonus and bonus not in player.values() and bonus not in opponent.values():
                        available.append(bonus)                        
                if hor>'a':
                    cap = (HOR[x-1],ver+i)
                    if cap in opponent.values():
                        captures.append(cap)
                if hor<'h':
                    cap = (HOR[x+1],ver+i)
                    if cap in opponent.values():
                        captures.append(cap)
            #en passant
            if self.moves:
                last = self.moves[-1]
                sides = ('w','b')
                side = sides[1-sides.index(last[0])]
                if last[0]=='w' and last[1][-1]=='4' or last[0]=='b' and last[1][-1]=='5':
                    if abs(ord(hor)-ord(last[1][0]))==1:
                        if ver==4 and side=='b':
                            enpassant.append((last[1][0],3))
                        elif ver==5 and side=='w':
                            enpassant.append((last[1][0],6))

            return available,captures,enpassant

        
        #double move and single move of pawns
        if player==white:
            if ver==2:
                return repeat(1,(hor,4))
            else:
                return repeat(1)
        else:
            if ver==7:
                return repeat(-1,(hor,5))
            else:
                return repeat(-1)
            

class Pieces:
    def __init__(self, size, board):
        self.size = size
        self.board = board
        self.moves = Moves()
        start = ((1,2),(8,7))
        elem1 = {'B':('c','f'),'N':('b','g'),'R':('a','h')}
        elem2 = {'K':'e','Q':'d'}
        pieces = [[],[]]
        self.white = {}
        self.black = {}
        self.active= None
        self.active_piece = None
        self.available = []
        self.captures = []
        self.enpassant = []

        self.castle_box = [[],[],[]]
        self.castle_move = 0
        self.castle_side = None

        self.threat = [0,0]

        self.all_moves = self.moves.moves

        for i,c in enumerate(('w','b')):
            for p in ('K','Q','B','N','R','P'):
                piece = pygame.image.load(PATH+p+c+'.png')
                piece = pygame.transform.scale(piece,[size]*2)
                pieces[i].append((p,piece))
        for i in range(2):
            for p,piece in pieces[i]:
                if i:
                    dict = self.black
                else:
                    dict = self.white
                if p=='P':
                    for x in range(8):
                        dict[(piece,x,p)] = (HOR[x],start[i][1])
                if p in ('K','Q'):
                    dict[(piece,0,p)] = (elem2[p],start[i][0])
                else:
                    for x in range(2):
                        if p in elem1:
                            dict[(piece,x,p)] = (elem1[p][x],start[i][0])
    
    def activate(self, key, player):
        x = player[key]
        if self.active==x:
            self.active = None
            self.active_piece = None
        else:
            self.active = x
            self.active_piece = key
            self.check_moves(key[2], x, player)
        
    def check_moves(self, piece:str, pos:tuple[int], player:dict, checking=0):
        if player==self.white:
            opponent = self.black
        else:
            opponent = self.white
        hor, ver = pos

        if not checking:
            self.available = []
            self.captures = []

        if opponent==self.white and not self.threat[0] or opponent==self.black and not self.threat[1]:
            if piece == 'R': 
                spaces = self.moves.rook(hor,ver)
            elif piece == 'N':
                spaces = self.moves.knight(hor,ver)
            elif piece == 'B':
                spaces = self.moves.bishop(hor,ver)
            elif piece == 'K':
                spaces, special, self.castle_side = self.moves.king(hor,ver,player,self.white)
                if special:
                    self.castle_move = 1
                for x in special:
                    if x in player.values():
                        self.castle_box[0].append(x)
                    elif x[0]=='b':
                        self.castle_box[2].append(x)
                    else:
                        self.castle_box[1].append(x)
                        
            elif piece == 'Q':
                spaces = self.moves.rook(hor,ver)
                spaces.extend(self.moves.bishop(hor,ver))
            else:
                self.available,captures,self.enpassant = self.moves.pawns(hor,ver,player,opponent,self.white)
                self.captures.extend(captures)
            if piece in ('K','N'):
                for x in spaces:
                    if x in opponent.values():
                        self.captures.append(x)
                    elif x not in player.values():
                        self.available.append(x)
            elif piece!='P':
                self.enpassant=[]
                for x in spaces:
                    for y in x:
                        if y in opponent.values():
                            self.captures.append(y)
                            break
                        elif y not in player.values():
                            self.available.append(y)
                        else:
                            break
            if piece!='K':
                if pos not in self.castle_box[0]:
                    self.castle_box=[[],[],[]]
                    self.castle_move = 0
        
    def move(self, dest, player):
        name = self.active_piece[2]
        if name=='P':
            self.all_moves.append(("w" if player==self.white else "b",f"{dest[0]}{dest[1]}"))
        else:
            self.all_moves.append(("w" if player==self.white else "b",f"{name}{dest[0]}{dest[1]}"))
        print(self.all_moves[-1])

        player[self.active_piece] = dest
        if name in ('K','R'):
            self.moves.castling[(self.white,self.black).index(player)] = 0
        self.active=None
        self.active_piece=None
        self.check(player)

    def capture(self, dest, player):
        name = self.active_piece[2]
        if name=='P':
            self.all_moves.append(("w" if player==self.white else "b",f"{player[self.active_piece][0]}x{dest[0]}{dest[1]}"))
        else:
            self.all_moves.append(("w" if player==self.white else "b",f"{name}x{dest[0]}{dest[1]}"))
        print(self.all_moves[-1])

        if player==self.white:
            opponent=self.black
        else:
            opponent=self.white
        player[self.active_piece] = dest
        if name in ('K','R'):
            self.moves.castling[(self.white,self.black).index(player)] = 0
        if self.enpassant:
            h = self.enpassant[0][0]
            for x,y in opponent.items():
                if y==(h,4) and opponent==self.white or y==(h,5) and opponent==self.black:
                    opponent[x]=dest
                    break
        self.active=None
        self.active_piece=None
        i=0
        while i<len(opponent):
            x=list(opponent.keys())[i]
            if opponent[x]==dest:
                del opponent[x]
                break
            i+=1
        self.check(player)
    
    def castle(self, dest, player):
        self.moves.castling[(self.white,self.black).index(player)] = 0
        if dest[0]<'e':
            self.all_moves.append(("w" if player==self.white else "b","O-O-O"))
            player[self.active_piece] = ('c',dest[1])
            for x in player:
                if player[x]==('a',dest[1]):
                    player[x] = ('d',dest[1])
        else:
            self.all_moves.append(("w" if player==self.white else "b","O-O"))
            player[self.active_piece] = ('g',dest[1])
            for x in player:
                if player[x]==('h',dest[1]):
                    player[x] = ('f',dest[1])
        self.active=None
        self.active_piece=None
        self.castle_box = [[],[],[]]
        self.castle_move = 0
        self.check(player)

    def check(self,player):
        z = [self.white,self.black]
        for player in z:
            opponent=self.white
            if player==self.white:
                opponent=self.black
        
            for x,y in player.items():
                self.check_moves(x[2],y,player,1)
            for x in opponent.keys():
                if x[2]=='K':
                    king = opponent[x]
            
            print(king, self.captures)
            if king in self.captures:
                if player==self.white:
                    self.threat[0]=1
                else:
                    self.threat[1]=1
            self.available=[]
            self.captures=[]
        
        # things to add here...


    def display(self, box_size):
        if self.active:
            hor, ver = self.active
            hor, ver = HOR.index(hor), VER.index(ver)

            colors = ((244,246,128),(187,204,68))
            box = pygame.Rect(0,0,*[box_size]*2)
            box.center = self.board[self.active][0].center
            pygame.draw.rect(screen,colors[hor%2^ver%2],box)

            for i in self.available+self.castle_box[1]+self.enpassant:
                dia = 26
                circle = pygame.Rect(0,0,dia,dia)
                circle.center = self.board[i][0].center
                pygame.draw.rect(screen,[x-25 for x in self.board[i][1]],circle,0,dia//2)
            for i in self.captures+self.castle_box[0]:
                hor, ver = i
                hor, ver = HOR.index(hor), VER.index(ver)
                colors2 = ((179,183,153),(77,107,45))
                box = pygame.Rect(0,0,*[box_size]*2)
                box.center = self.board[i][0].center
                pygame.draw.rect(screen,colors2[hor%2^ver%2],box,7,box_size//2)
            
        for x in (self.white,self.black):
            for piece in x:
                rect = piece[0].get_rect()
                rect.center = self.board[x[piece]][0].center
                screen.blit(piece[0],(rect.x,rect.y))


class Game:
    def __init__(self):
        self.Board = Board(680,(10,10))
        self.Pieces = Pieces(80, self.Board.board)
        self.run()

    def display(self):
        self.Board.display()
        self.Pieces.display(self.Board.size//8)

    def run(self):
        turn = 0
        while True:
            screen.fill((0,0,0))
            for ev in pygame.event.get():
                if ev.type==QUIT:
                    pygame.quit()
                    exit()
                elif ev.type==MOUSEBUTTONUP:
                    # selecting the player
                    if turn:
                        player = self.Pieces.black
                    else:
                        player = self.Pieces.white

                    # activates and deactivates a piece
                    for x in self.Board.board:
                        if self.Board.board[x][0].collidepoint(pygame.mouse.get_pos()):
                            for y in player:
                                if player[y]==x:
                                    if self.Pieces.castle_move and y[2]=='R':
                                        if player[y][0] not in self.Pieces.castle_side:
                                            self.Pieces.castle_move = 0
                                            self.Pieces.castle_box = [[],[],[]]
                                            self.Pieces.castle_side = None
                                            self.Pieces.activate(y, player)
                                    else:
                                        self.Pieces.activate(y, player)

                    # moves a piece, or captures a piece, or castles the king
                    if self.Pieces.active:
                        for x in self.Pieces.available:
                            if self.Board.board[x][0].collidepoint(pygame.mouse.get_pos()):
                                self.Pieces.move(x, player)
                                turn=1-turn
                        for x in self.Pieces.captures+self.Pieces.enpassant:
                            if self.Board.board[x][0].collidepoint(pygame.mouse.get_pos()):
                                self.Pieces.capture(x, player)
                                turn=1-turn
                        for x in self.Pieces.castle_box:
                            for y in x:
                                if self.Board.board[y][0].collidepoint(pygame.mouse.get_pos()):
                                    self.Pieces.castle(y,player)
                                    turn=1-turn

                elif ev.type==KEYUP:
                    if ev.key==K_SPACE:
                        self.Board.revolve()
            
            self.display()
            pygame.display.update()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()

######################### check determination done ##############################
######################## check removal moves to add ##############################