import pygame
import sys
import random
import copy

modify = {'covered': 18.164223401662543, 'height': 14.147529323390039, 'twospace': 18.090152798727715, 'edgespace': 3.4974238280685697}
#modify = {'covered': 20, 'uncovered': 20, 'height': 10, 'twospace': 10}
        
def has_landed(board, points): # return boolean
    
    for point in points:
        # if landed on border
        if point[0] + 1 > 19: return True
        # if landed on block
        if board[point[0] + 1][point[1]] != 'grey': return True
    return False

def move_down(points): # return points
    
    for i in range(len(points)): 
        points[i][0] += 1
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
    for i in range(len(points)):
        points[i][1] -= left - x
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
        if right > 9: points[i][1] -= right - 9
            
    # checks of rotation conflicts with blocks
    temp_line = board[0]
    board[0:18] = board[1:19]
    board[19] = temp_line

    if has_landed(board, points): 
        return p
    return points
        
        
def get_board_points(board):
    
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
                    
                    if board[y2][x] != 'grey': score += (len(board) - y2) * modify['covered']
                    #else: score += (len(board) - y2) * modify['uncovered']
        
        # inside twospace
        for x, color in enumerate(board[y][1:-1]):
            
            if board[y][x - 1] != 'grey' and color == 'grey' and board[y][x + 1] != 'grey': score += (len(board) - y) * modify['twospace']
                
        # outside two space
        if board[y][0] == 'grey' and board[y][1] != 'grey': score += (len(board) - y) * modify['twospace']
        if board[y][9] == 'grey' and board[y][8] != 'grey': score += (len(board) - y) * modify['twospace']
            
    return score
        
def get_best_move(block, b):
    
    # point system: empty square under = - 20, high squares = - 1 * square level
    
    best = [-1, 1e10, 0]
    
    for rot in range(4):
        
        bottom, left, top, right = get_bounds(block)
        
        for x in range(10 - right + left):
            
            dummy = copy.deepcopy(block)
            board = copy.deepcopy(b)
            
            dummy = set_position(x, dummy)
            dummy = fall(board, dummy)
            
            # appends block to board
            for point in dummy: board[point[0]][point[1]] = 'red'
                    
            # removes tetris lines
            tetris_check = True
            while tetris_check: tetris_check, board = tetris_board(board)
            
            if best[1] > get_board_points(board): best = [x, get_board_points(board), rot]
        
        block = rotate(board, block)
    
    bottom, left, top, right = get_bounds(block)
        
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

def play_tetris():

    # window variables
    resolution = (300, 512)
    pygame.init()
    clock = pygame.time.Clock()
    surface = pygame.display.set_mode(resolution)
    pygame.display.set_caption('Tetris')
    game_running = True
    fps = 3000

    # tetris board variables
    board = [['grey' for j in range(10)] for i in range(20)]
    side_length = resolution[1] // 24
    
    block_color, block = get_color(), get_shape()
    position, rotation = get_best_move(block, board)
    
    lines_cleared = 0

    while game_running:
        
        if rotation > 0: 
            block = rotate(board[:], block)
            rotation -= 1
        elif position > 0: 
            block = shift(1, board, block)
            position -= 1
        elif position < 0: 
            block = shift(-1, board, block)
            position += 1
        else: 
            block = fall(board, block)
        
        #print(position, rotation)

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
            position, rotation = get_best_move(block, board)
                    
        else:
            block = move_down(block)
        
        # render and clock
        pygame.display.flip()
        clock.tick(fps)
        
    print(lines_cleared)
    
while True:
    play_tetris()