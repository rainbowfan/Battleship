#This program implements a one player version of battleship that allows the user to play against
#an AI. In this program, the board size, the number and size of the ships are specified by users

import random
import sys


def is_valid_integer(integer):
    """
    checks to see if input represents a valid integer
    @input: string-type object
    @output: True if it is integer, False otherwise
    """
    integer = integer.strip()
    if len(integer) == 0:
        return False
    else:
        return (integer.isdigit() or #positive integer
                (integer.startswith('-') and integer[1:].isdigit())) #negative integer


def get_seed():
    """allows user to specify the seed.
       check the seed and convert it into integer
       @output seed(integer)
    """
    seed = ''
    while not is_valid_integer(seed):
        seed = input('Enter the seed: ')
    return int(seed)


def is_valid_files(filename, width, height):
    """
    This function reads ship placement files and checks whether they are structured correctly
    If ships are not placed correctly, warning messages will be displayed and the program will
    terminate
    @input: filename, width, height
    @output: returns varified contect of the file or program terminates
    """
    with open(filename) as file:
        contents = file.readlines() #contents is a list
        ship_symbol = []
        ship_position = []
        for i in contents:
            info = i.split()
            if info[0] in ['x', 'X', 'o', 'O', '*']: 
               print('Error symbol %s is already in use. Terminating game.'%(info[0]))
               sys.exit(0)
            ship_symbol.append(info[0])

              
            #should include all the internal points
            if info[1] == info[3] and int(info[2]) < int(info[4]):
               for y in range(int(info[2]),(int(info[4])+1)):
                   if (int(info[1]), y) in ship_position:
                       print('There is already a ship at location %d, %d.'% (int(info[1]), y), 'Terminating game.')
                       sys.exit(0)
                   else: ship_position.append((int(info[1]), y))
            elif info[1] == info[3] and int(info[2]) > int(info[4]):
                for y in range(int(info[4]),(int(info[2])+1)):
                   if (int(info[1]), y) in ship_position:
                       print('There is already a ship at location %d, %d.'% (int(info[1]), y), 'Terminating game.')
                       sys.exit(0)
                   else: ship_position.append((int(info[1]), y))
            elif info[2] == info[4]:
                for x in range(int(info[1]),(int(info[3])+1)):
                    if (x, int(info[2])) in ship_position:
                        print('There is already a ship at location %d, %d.' %(x, int(info[2])), 'Terminating game.')
                        sys.exit(0)
                    else: ship_position.append((x, int(info[2])))
            else:
                 print('Ships cannot be placed diagonally. Terminating game.')
                 sys.exit(0)

            if int(info[1])<0 or int(info[1])>(height-1) or int(info[2])<0 or int(info[2]) >(width-1) or int(info[3]) <0 or int(info[3]) >(height-1) or int(info[4])<0 or int(info[4])>(width-1):
               print('Error %s is placed outside of the board. Terminating game.'%(info[0]))
               sys.exit(0)
               
        for i in ship_symbol:
            if ship_symbol.count(i) >1:
                print('Error symbol %s is already in use. Terminating game'%(i))
                sys.exit(0)
        return contents #contents is a list in which each line is an element   

def oneship_update_onboard(board, symbol, x_start, x_end, y_start, y_end): #board updated by specifying start and end points of one ship, coordinates are integers
     """
     this function update board for one ship
     @input: board-list, symbol-symbol for the ship, x_start, y_start: start point of the ship, x_end, y_end:end point of the ship
     @return: updated board
     """
     if x_start == x_end: #check whethe the ship is placed horizontally
            board[x_start+1][(y_start+1):(y_end+2)] = symbol*(y_end-y_start+1)
     else:
        for i in range(len(board)):
            if i >= (x_start+1) and i <= (x_end+1):
                board[i][y_start+1] = symbol #complete storing ships
        
     return board 

def my_board_setup(width, height, contents): #used to construct my board
    board = []
    for i in range(height+1):
        board.append([])
    for i in board:
        for j in range(width+1):
            i.append('*')
    board[0][1:] = range(width)#add coordinate label
    for i in range(height):
        board[i+1][0] = i #add coordinate label
    board[0][0] = ' '
    ###my board complete

    #update myboard by adding ships on myboard
    for point in contents:
        symbol = point.split()[0]
        x_start = int(point.split()[1])
        y_start = int(point.split()[2]) 
        x_end = int(point.split()[3])
        y_end = int(point.split()[4])
        revise_ystart = 0
        revise_yend = 0
        
        if y_start > y_end: #consider special case in which the end and beginning of the ship should be switched
            revise_ystart = y_end
            revise_yend = y_start
            y_start = revise_ystart
            y_end = revise_yend
        
        board = oneship_update_onboard(board, symbol, x_start, x_end, y_start, y_end) 
    return board #complete the board set up and ship placements


def is_valid_input(player_fired, width, height, fire_xy): 
    """
    this function checks whether the user-specified firing coordinates are valid
    @player_fired: a list containing all the previous shooting positions of the player
    @fire_xy: user-specified new shooting position--a string in the row space colum form. eg. '1 2'
    @return False if it is not a valid target
    """
    if len(fire_xy.split()) !=2:
        return False
    fire_x = fire_xy.split()[0]
    fire_y = fire_xy.split()[1]
    if fire_x.isdigit()==False or fire_y.isdigit()==False:
        return False
    if int(fire_x)>(height-1) or int(fire_y)>(width-1):
        return False
    if (int(fire_x), int(fire_y)) in player_fired:
        return False
    
def display_board(board):
    """
    this function displays board which is a list
    """
    for i in board:
        for j in range(len(i)):
            if j == (len(i)-1):
                print(i[j])
            else:
                print(i[j], end = ' ')
   
def play_game(board, xy_input, potential_pts, num_ships, board_copy, ship_symbol_num):
    """
    this function implements the battleship game
    @board: list used to check ships on it.
    @xy_input: row space column form eg.'2 3' representing a target
    @potential_pts: a list containing all the valid shooting positions(each pair is a tuple)
    @num_ships: integer representing total number of ships
    @board_copy:list used to show the shooting position 
    """
    pt_x = int(xy_input.split()[0])
    pt_y = int(xy_input.split()[1])
    num_hit = 0

    for i in board_copy:
         num_hit += sum(j =='X' for j in i) #calculate total number of hits before shooting
          
    if board[pt_x+1][pt_y+1] == '*':  #this is case that player fails to shoot the target
       board_copy[pt_x+1][pt_y+1]='O' #update the board with 'O' 
       potential_pts.remove((pt_x, pt_y)) #remove the target from potential points list
       print('Miss!')
    elif board[pt_x+1][pt_y+1] not in ['O', 'X', '*']:  #this is the case that player shoots the target successfully
       symbol = board[pt_x+1][pt_y+1] #extract the ship symbol
       board_copy[pt_x+1][pt_y+1]='X' #update the board with 'X' representing hit
       ship_symbol_num[symbol] -=1 #the length of the ship goes down 
       potential_pts.remove((pt_x, pt_y)) #remove the shooting position from potential points list 
       num_hit+=1  #update hit number
       if ship_symbol_num[symbol] == 0 : #check whether the game will end after this ship sinks
           print('You sunk my %s'%(symbol))
       else:
           print('Hit!')
    return num_hit #return total number of hits
    
        
    
def AI_fire(AI_type, AI_potential_pts, myboard, width, height, candidate_pts_destroy, cheating_pts):
    """
    this function implements 3 different AIs and shows their strategy when playing the game
    Different types of AIs have different stragies in the game.
    @AL_potential_pts: a list containing all the posible target that AI can choose to shoot
    target got removed from the list once AI shoots the position already
    @return: point(a tuple) that the specified AI will choose to shoot
    """
    if AI_type ==1: #random AI
        pts = random.choice(AI_potential_pts) #choose shooting target from potential list
        
    elif AI_type ==2: #smart AI has two modes: hunt and destroy-hunt is the same as random AI. It will switch to destroy once scores a hit 
        if len(candidate_pts_destroy) == 0: #in the beginning or return to the Hunt mode when shooting positions for Destroy mode are exhausted.
           pts = random.choice(AI_potential_pts) #hunt works the same as random AI
           pt_x = pts[0]
           pt_y = pts[1]
           
           if myboard[pt_x+1][pt_y+1] not in ['o', 'O', 'X', 'x', '*']: #if hit, AI switches to Destroy Mode
              if (pt_x -1) >=0 and (pt_x-1, pt_y) in AI_potential_pts and candidate_pts_destroy.count((pt_x-1, pt_y))== 0: #check valid points by order-once verified, the point will be added on the target list for destroy mode       
                  candidate_pts_destroy.append((pt_x-1, pt_y))    
              if (pt_x+1) < height and (pt_x+1, pt_y) in AI_potential_pts and candidate_pts_destroy.count((pt_x+1, pt_y))== 0: #check point below
                  candidate_pts_destroy.append((pt_x+1, pt_y))
              if (pt_y-1) >=0 and (pt_x, pt_y-1) in AI_potential_pts and candidate_pts_destroy.count((pt_x, pt_y-1))== 0:#check point to its left
                  candidate_pts_destroy.append((pt_x, pt_y-1))
              if (pt_y+1) < width and (pt_x, pt_y+1) in AI_potential_pts and candidate_pts_destroy.count((pt_x, pt_y+1))== 0: #check point to its right
                  candidate_pts_destroy.append((pt_x, pt_y+1))
        else:
            pts = candidate_pts_destroy[0] #if list of shooting positions for destroy mode are not exhausted, stay in destroy mode
            pt_x = pts[0]
            pt_y = pts[1]        
            candidate_pts_destroy.remove(pts) #remove the point once destroy AI already shoot it
            if myboard[pt_x+1][pt_y+1] not in ['o', 'O', 'X', 'x', '*']: #if scores a hit, check potential positions by order
               if (pt_x -1) >=0 and (pt_x-1, pt_y) in AI_potential_pts and candidate_pts_destroy.count((pt_x-1, pt_y))== 0 :
                   candidate_pts_destroy.append((pt_x-1, pt_y))    
               if (pt_x+1) < height and (pt_x+1, pt_y) in AI_potential_pts and candidate_pts_destroy.count((pt_x+1, pt_y))== 0 :
                   candidate_pts_destroy.append((pt_x+1, pt_y))
               if (pt_y-1) >=0 and (pt_x, pt_y-1) in AI_potential_pts and candidate_pts_destroy.count((pt_x, pt_y-1))== 0 :
                   candidate_pts_destroy.append((pt_x, pt_y-1))
               if (pt_y+1) < width and (pt_x, pt_y+1) in AI_potential_pts and candidate_pts_destroy.count((pt_x, pt_y+1))== 0 :
                   candidate_pts_destroy.append((pt_x, pt_y+1))
    else: #cheating AI
       pts = cheating_pts[0] #ship positions from myboard are saved in the list
       cheating_pts.remove(pts) #remove from the list, once AI shoots it
    return pts #return shooting position(tuple)

def deep_copy(orig): #deep copy a nested list
    if isinstance(orig, list):
        new = []
        for item in orig:
            new.append(deep_copy(item))
        return new
    else:
        return orig
   
def main():
    """
    this function gathers things together to finish the battleship game
    """
    seed = get_seed()
    random.seed(seed)
    
    width = ''
    while not width.isdigit() or width == '0':
        width = input('Enter the width of the board: ').strip()
    width = int(width)
    
    height = ''
    while not height.isdigit() or height == '0':
        height = input('Enter the height of the board: ').strip()
    height = int(height)

    
    filename = input('Enter the name of the file containing your ship placements:\n').strip()

    AI_type = '' #ask use to retype AI type when the input is not valid
    while not AI_type.isdigit() or int(AI_type)== 0 or int(AI_type) >3:
          print('Choose your AI.\n1. Random\n2. Smart\n3. Cheater')
          AI_type = input(' Your choice: ').strip()
    AI_type = int(AI_type)
    
    contents = is_valid_files(filename, width, height) #check the filenmame. Once raising warnings, the program will terminate. Otherwise it will return the contents as a list in which each line is a string
    
    myboard = my_board_setup(width, height, contents) #set up my board
    
    AIboard = [] #create AI board
    for i in range(height+1):
        AIboard.append([])

    for i in AIboard:
        for j in range(width+1):
            i.append('*')
    AIboard[0][1:] = range(width)#add coordinate labels
    for i in range(height):
        AIboard[i+1][0] = i #add coordinate labels
    AIboard[0][0] = ' '

    
    contents = sorted(contents) #contents is a list in which each element is a string(one ship)
    num_ships = 0
    result1 = 0
    result2 = 0
    player_symbol_num = {}
    AI_symbol_num = {}
    
    #calculate length of each ship and add them up to get total number of ships
    for ship in contents:
        symbol = ship.split()[0]
        x_start = int(ship.split()[1])
        x_end = int(ship.split()[3])
        y_start = int(ship.split()[2])
        y_end = int(ship.split()[4])
        
        
        if x_start != x_end:
            length = abs(x_start-x_end)+1
        else:
            length = abs(y_start-y_end)+1
            
            
        player_symbol_num[symbol] = length
        AI_symbol_num[symbol] = length #add symbol and corresponding length of ships as key-value pairs in the dictionary
        num_ships += length
        
        #AI will use same ships but position them differently
        place = False
        
        while place == False: #when same position is selected again, the positioning direction and starting point for the ship will be randomly chosen again
           choice = random.choice(['vert','horz']) 
           if choice == 'horz':
              max_col = width - length
              x_start = random.randint(0, (height-1))
              y_start = random.randint(0, max_col)
              y_end = y_start+length-1 
              x_end = x_start
              if length==0:
                  x_end = x_start
                  y_end = y_start
              if AIboard[x_start+1][(y_start+1):(y_end+2)] == ['*']*(length):  #check whether other ships are on these positions already.
                    place = True 
              else:
                    place = False #if it is occupied by other ships, both direction and starting point will be selected randomly again 
               
           elif choice == 'vert':
              max_row = height - length
              x_start = random.randint(0, max_row)
              y_start = random.randint(0, (width-1))
              x_end = x_start+length-1
              y_end = y_start
              if length==0:
                  x_end = x_start
                  y_end = y_start
              check = []
              for x in range(x_start,(x_end+1)):
                 check.append(AIboard[x+1][y_end+1]) 
              if check == ['*']*length:
                  place = True
              else:
                  place = False
       
        AIboard = oneship_update_onboard(AIboard, symbol, x_start, x_end, y_start, y_end) #update AI board after getting the position of a ship
        print('Placing ship from %d,%d to %d,%d.'%(x_start, y_start, x_end, y_end))
        
    AIboard_screen = deep_copy(AIboard) #deepcopy AIboard. AIboard_screen is used for scanning purpose while AIboard is used to check whether 'O' or 'X' should be placed on the same position on ALboard_screen
    
    for i in AIboard_screen: #after deepcopy, clean corresponding entries by '*'
        for j in range(len(i)):
            if j !=0 and i != AIboard_screen[0]:
               i[j] = '*'           
                   
    AI_potential_pts = []
    cheating_pts = []
    player_fired = []

    for i in range(height):  #list of locations are generated by row and then column
        for j in range(width):
            AI_potential_pts.append((i,j))
            if myboard[i+1][j+1] != '*':
                cheating_pts.append((i,j)) #store ship positions on myboard for cheating AI
    

    player_potential_pts = AI_potential_pts.copy()       
    candidate_pts_destroy = []
    first_player = random.randint(0,1)
    
    for round in range(width*height*2): #start to play the game
        fire_xy = ''
        result1 =0
        result2 =0
        
        player = (first_player + round)%2 #player and AI play the game alternatively
        if player == 0: #player's turn
           print('Scanning Board')
           display_board(AIboard_screen)
           print()
           print('My Board')
           display_board(myboard)
           print()
            
           while is_valid_input(player_fired, width, height, fire_xy)== False: 
             fire_xy = input('Enter row and column to fire on separated by a space: ').strip()
           new_pts = fire_xy.split()
           player_fired.append((int(new_pts[0]), int(new_pts[1])))
           result1 = play_game(AIboard, fire_xy, player_potential_pts, num_ships, AIboard_screen,player_symbol_num)
           
        else: #AI's turn
           pts = AI_fire(AI_type, AI_potential_pts, myboard, width, height, candidate_pts_destroy, cheating_pts) #shooting position selected by specified AI
           fire_xy = str(pts[0])+' '+str(pts[1])
           print('The AI fires at location', pts)
           result2 = play_game(myboard, fire_xy, AI_potential_pts,num_ships, myboard, AI_symbol_num) #return number of hits
           
        if result1 == num_ships or result2 == num_ships: #check whether the game ends after this round
            break
        
    print('Scanning Board')
    display_board(AIboard_screen)
    
    print()
    print('My Board')
    display_board(myboard)
    print()

    if result1==num_ships:
        print('You win!')
            
    else:
        print('The AI wins.')
            
                    
main()           
            
            
            














