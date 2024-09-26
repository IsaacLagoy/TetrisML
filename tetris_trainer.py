import random
import copy
import threading

class shape():
    
    def __init__(self, color = 'yellow', points = [[0,0], [1,0], [0,1], [1,1]]):
        
        self.color = color
        self.points = points
        
    def has_landed(self, board):
        
        for point in self.points:
            # if landed on border
            if point[0] + 1 > 19: return True
            # if landed on block
            if board[point[0] + 1][point[1]] != 'grey': return True
        return False
    
    def move_down(self):
        
        for i in range(len(self.points)):
            self.points[i][0] += 1
            
    def set_position(self, x):
        
        bottom, left, top, right = self.get_bounds(self.points)
        for i in range(len(self.points)):
            self.points[i][1] -= left - x
            
    def shift(self, amount, board):
    
        for i in range(len(self.points)):
            if not 0 <= self.points[i][1] + amount <= 9: return
            if board[self.points[i][0]][self.points[i][1] + amount] != 'grey': return
        for i in range(len(self.points)):
            self.points[i][1] += amount
            
    def fall(self, board):
        
        while not self.has_landed(board):
            self.move_down()
            
    def get_bounds(self, points):
        
        bottom, left, top, right = 0, 1e2, 1e2, 0
        for point in points:
            if bottom < point[0]: bottom = point[0]
            if top > point[0]: top = point[0]
            if left > point[1]: left = point[1]
            if right < point[1]: right = point[1]
            
        return bottom, left, top, right
            
    def rotate(self, board):
        
        points = self.points[:]
        # gets bottom left point of block
        
        # moves block into correct orientation
        bottom, left, top, right = self.get_bounds(points)
        for i, point in enumerate(points):
            points[i] = [point[1] - left, top - point[0]]
            
        # moves block into correct position
        b, l, t, r = self.get_bounds(points)
        
        for i, point in enumerate(points):
            points[i] = [point[0] + (bottom - b), point[1] + (left - l)]
            
        # moves shape back into bounds
        right = 0
        for point in points:
            if right < point[1]: right = point[1]
            
        for i in range(len(points)):
            if right > 9: points[i][1] -= right - 9
            
        # checks of rotation conflicts with blocks
        temp = board[0]
        board[0:18] = board[1:19]
        board[19] = temp
        temp_points = self.points[:]
        self.points = points[:]
        if self.has_landed(board): self.points = temp_points[:]
        
def get_board_points(board, modify):
    
    # shortens board to minimum height
    minimum = 0
    for y in range(len(board)):
        for x, color in enumerate(board[y]):
            if color != 'grey': break
        else: continue
        break
    
    board = board[minimum:]
    
    score = 0
    
    # first line
    for color in board[0]:
        if color != 'grey': score += len(board)
    
    # rest of lines
    for y in range(1, len(board)):
        
        for x, color in enumerate(board[y]):
            
            if color != 'grey': score += (len(board) - y) * modify['height']
            else: 
                for y2 in range(0, y):
                    if board[y2][x] != 'grey': score += (len(board) - y) * modify['covered']
                    else: score += (len(board) - y) * modify['uncovered']
                    
        for x, color in enumerate(board[y][1:-1]):
            
            if board[y][x - 1] != 'grey' and color == 'grey' and board[y][x + 1] != 'grey': 
                score += (len(board) - y) * modify['twospace']
            
    return score
        
def get_best_move(block : shape, b, modify):
    
    # point system: empty square under = - 20, high squares = - 1 * square level
    
    best = [-1, 1e10, 0]
    d = copy.deepcopy(block)
    
    for rot in range(4):
        
        bottom, left, top, right = d.get_bounds(d.points)
        
        for x in range(10 - right + left):
            
            dummy = copy.deepcopy(d)
            board = copy.deepcopy(b)
            
            dummy.set_position(x)
            dummy.fall(board)
            
            # appends block to board
            for point in dummy.points: board[point[0]][point[1]] = 'red'
                    
            # removes tetris lines
            tetris_check = True
            while tetris_check: tetris_check, board = tetris_board(board)
            
            points = get_board_points(board, modify)
            if best[1] > points: best = [x, points, rot]
        
        d.rotate(board)
    
    bottom, left, top, right = block.get_bounds(block.points)
        
    return best[0] - left, best[2]
            
def get_color():
    
    return random.choice([
        'red',
        'orange',
        'yellow',
        'green',
        'blue',
        'purple'
    ])

def get_shape():
    
    return random.choice([
        [[0,4], [1,4], [0,5], [1,5]],
        [[0,4], [1,4], [2,4], [3,4]],
        [[0,5], [0,6], [1,4], [1,5]],
        [[0,4], [0,5], [1,5], [1,6]],
        [[0,4], [1,4], [2,4], [2,5]],
        [[0,5], [1,5], [2,5], [2,4]],
        [[0,4], [0,5], [0,6], [1,5]]
               ])

# checks for a tetris
def tetris_board(board):
    
    for y in range(len(board)):
        
        line_full = True
        for color in board[y]:
            if color == 'grey':
                line_full = False
                break
        
        if line_full:
            board[1:y + 1] = board[0:y]
            board[0] = ['grey' for j in range(10)]
            return True, board
    return False, board

def play_tetris(modify):
    
    random.seed(1)

    game_running = True

    # tetris board variables
    board = [['grey' for j in range(10)] for i in range(20)]
    
    block = shape(get_color(), get_shape())
    position, rotation = get_best_move(copy.deepcopy(block), board[:], modify)
    
    lines_cleared = 0

    while game_running:
        
        if rotation > 0: 
            block.rotate(board[:])
            rotation -= 1
        elif position > 0: 
            block.shift(1, board)
            position -= 1
        elif position < 0: 
            block.shift(-1, board)
            position += 1
        else: block.fall(board)
        
        #print(position, rotation)
                
        # dropping
        if block.has_landed(board):
                
            # if loss
            for point in block.points:
                if point[0] == 0: game_running = False
                        
            # appends block to board
            for point in block.points:
                board[point[0]][point[1]] = block.color
                    
            # removes tetris lines
            tetris_check = True
            while tetris_check:
                tetris_check, board = tetris_board(board[:])
                if tetris_check: lines_cleared += 1
                    
            # creates new block
            block = shape(get_color(), get_shape())
            # bot being dumb
            position, rotation = get_best_move(copy.deepcopy(block), board[:], modify)
                    
        else:
            block.move_down()
        
    outputs.append((lines_cleared, modify))
    
outputs = []
master = {'covered': 19.65241774296711, 'uncovered': -0.15967625148400866, 'height': 19.649805798509576, 'twospace': 10.488563420675824}
high = (0, {'covered': 19.65241774296711, 'uncovered': -0.15967625148400866, 'height': 19.649805798509576, 'twospace': 10.488563420675824})
    
while True:
    
    temp = {}
    random.seed()
    for key, value in master.items():
        temp[key] = value + random.uniform(-1.0, 1.0)
    threading.Thread(target = play_tetris, args = (temp,)).start()
    
    """random.seed()
    for i in range(30):
        temp = {}
        for key, value in master.items():
            temp[key] = value + random.uniform(0,0)
        threading.Thread(target = play_tetris, args = (temp,)).start()"""
    
    while threading.active_count() > 1: #print(threading.active_count())
        
        pass
    
    print(outputs[-1][0])
    for i in range(len(outputs)):
        if outputs[i][0] > high[0]: 
            high = outputs[i]
            print(high[0], high[1])
    
    #outputs = []
    master = high[1]          