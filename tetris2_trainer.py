# adds block sliding, seeded training, faster run speed - triple testing sliding

import pygame
import sys
import random
import copy
        
def has_landed(board, points): # return boolean
    
    for point in points:
        # if landed on border
        if point[0] + 1 > 19: return True
        # if landed on block
        if board[point[0] + 1][point[1]] != 'grey': return True
    return False

def move_down(points): # return points
    
    for i in range(len(points)): points[i][0] += 1
    return points

def get_bounds(points): # returns rectangular bounds of array
        
    bottom, left, top, right = 0, 1e2, 1e2, 0
    
    for point in points:
        if bottom < point[0]: bottom = point[0]
        if top > point[0]: top = point[0]
        if left > point[1]: left = point[1]
        if right < point[1]: right = point[1]
            
    return bottom, left, top, right

def set_position(x, points): # return points
        
    bottom, left, top, right = get_bounds(points)
    for i in range(len(points)): points[i][1] += x - left
    return points

def shift(amount, board, points): # return shifted points
    
        for i in range(len(points)):
            if not 0 <= points[i][1] + amount <= 9: return points
            if board[points[i][0]][points[i][1] + amount] != 'grey': return points
        for i in range(len(points)):
            points[i][1] += amount
        
        return points
    
def fall(board, points): # returns points at lowest location
        
    while not has_landed(board, points):
        points = move_down(points)
        
    return points

def rotate(board, p):
        
    points = p[:]
    # moves block into correct orientation
    bottom, left, top, right = get_bounds(points)
    for i, point in enumerate(points):
        points[i] = [point[1] - left, top - point[0]]
            
    # moves block into correct position
    b, l, t, r = get_bounds(points)
        
    for i, point in enumerate(points):
        points[i] = [point[0] + (bottom - b), point[1] + (left - l)]
            
    # moves shape back into bounds
    right = 0
    for point in points:
        if right < point[1]: right = point[1]
            
    for i in range(len(points)):
        if right > 9: points[i][1] += 9 - right
            
    # checks of rotation conflicts with blocks
    temp_line = board[0]
    board[0:18] = board[1:19]
    board[19] = temp_line

    if has_landed(board, points): 
        return p
    return points
        
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
    
    # rest of lines
    for y in range(0, len(board)):
        
        for x, color in enumerate(board[y]):
            
            # increases score based off block height
            if color != 'grey': 
                score += (len(board) - y) * modify['height']
            else: 
                for y2 in range(0, y):
                    
                    # if a hole is covered my another block
                    if board[y2][x] != 'grey': 
                        score += (len(board) - y) * modify['covered']
                        break
        
        # inside twospace
        for x, color in enumerate(board[y][1:-1]):
            
            if board[y][x - 1] != 'grey' and color == 'grey' and board[y][x + 1] != 'grey': 
                score += (len(board) - y) * modify['twospace']
                
        # outside two space
        if board[y][0] == 'grey' and board[y][1] != 'grey': score += (len(board) - y) * modify['edgespace']
        if board[y][9] == 'grey' and board[y][8] != 'grey': score += (len(board) - y) * modify['edgespace']
            
    return score

def get_best_move(block, b, modify):
    
    # point system: empty square under = - 20, high squares = - 1 * square level
    
    best = [-1, 1e10, 0, 0]
    
    for rot in range(4):
        
        bottom, left, top, right = get_bounds(block)
        
        shifted_states = []
        
        for x in range(10 - right + left):
            
            # lowers block into position
            dummy = copy.deepcopy(block)
            board = copy.deepcopy(b)
            
            dummy = set_position(x, dummy)
            dummy = fall(board, dummy)
            
            # adds in shift
            
            for s in [0, -1, 1]:
            
                shift_dummy = copy.deepcopy(dummy)
                dummy_board = copy.deepcopy(board)
                shift_dummy = shift(s, dummy_board, shift_dummy)
                
                # appends block to board
                for point in shift_dummy: dummy_board[point[0]][point[1]] = 'red'
                        
                # removes tetris lines
                tetris_check = True
                while tetris_check: tetris_check, dummy_board = tetris_board(dummy_board)
                
                if get_bounds(shift_dummy) in shifted_states: continue # if shift did not affect anything
                
                points = get_board_points(dummy_board, modify)
                
                if best[1] > points: best = [x, points, rot, s]
                
                # adds shifted state to list
                shifted_states.append(get_bounds(shift_dummy))
        
        block = rotate(board, block)
    
    bottom, left, top, right = get_bounds(block)
        
    return best[0] - left, best[2], best[3]
            
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

def play_tetris(modify, seed):
    
    random.seed(seed)

    # window variables
    resolution = (300, 512)
    pygame.init()
    surface = pygame.display.set_mode(resolution)
    pygame.display.set_caption('Tetris')
    game_running = True

    # tetris board variables
    board = [['grey' for j in range(10)] for i in range(20)]
    side_length = resolution[1] // 24
    
    block_color, block = get_color(), get_shape()
    position, rotation, end_shift = get_best_move(block[:], board, modify)
    
    lines_cleared = 0

    while game_running:
        
        #check = False
        if rotation > 0: 
            block = rotate(board[:], block[:])
            rotation -= 1
        elif position > 0: 
            block = shift(1, board, block)
            position -= 1
        elif position < 0: 
            block = shift(-1, board, block)
            position += 1
        else: 
            block = fall(board, block)
            block = shift(end_shift, board, block)
            end_shift = 0
            
        #print(get_bounds(block))
        #print(position, rotation, '\n')

        # allows program to quit 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                sys.exit()
                
        # reset
        surface.fill('black')
        
        # display board
        for y in range(len(board)):
            for x, color in enumerate(board[y]):
                
                # rect = x, y, w, h
                pygame.draw.rect(surface, color, pygame.Rect(resolution[0]//2 - side_length * 5 + x * side_length, side_length * 2 + y * side_length, side_length-1, side_length-1))
                
        # display block
        for point in block:
            pygame.draw.rect(surface, block_color, pygame.Rect(resolution[0]//2 - side_length * 5 + point[1] * side_length, side_length * 2 + point[0] * side_length, side_length-1, side_length-1))
                
        # dropping
            
        if has_landed(board, block):
                
            # if loss
            for point in block:
                if point[0] == 0: game_running = False
                        
            # appends block to board
            for point in block:
                board[point[0]][point[1]] = block_color
                    
            # removes tetris lines
            tetris_check = True
            while tetris_check:
                tetris_check, board = tetris_board(board)
                if tetris_check: lines_cleared += 1
                    
            # creates new block
            block_color, block = get_color(), get_shape()
                
            # bot being dumb
            position, rotation, end_shift = get_best_move(block, board, modify)
                    
        else:
            block = move_down(block)
        
        # render and clock
        pygame.display.flip()
    
    print(lines_cleared)
    return lines_cleared
    
master = {'covered': 20.3070618279345, 'height': 13.12836380198535, 'twospace': 14.956531749040089, 'edgespace': 3.3520076371042626}
#master = {'covered': 10, 'height': 5, 'twospace': 0, 'edgespace': 0}
high = (0, master)

while True:
    
    seed = random.randint(1,1000)
    for i in range(20):
        
        random.seed()
        temp = {}
        for key, value in master.items():
            temp[key] = value + random.uniform(-1.0, 1.0)
            
        score = play_tetris(temp, seed)
        
        if score > high[0]: high = (score, temp)
    
    master = high[1]
    
    print(high)
    
    high = (0, master)
