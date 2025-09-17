import random
import os
import time
import threading

import termios
import sys
import tty

from typing import Optional

BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  # Resets to default terminal text color

fruits = ("🍎", "🍊", "🍋", "🥝", "🫐 ", "🍇")


matrix = {}

grid_x = 10
grid_y = 10
select_x = round(grid_x / 2)
select_y = round(grid_y / 2)
prev_x = None
prev_y = None
score = 0

refresh = True
clearing = False

if os.name == "nt":
    import msvcr

def update_terminal(message: str = None) -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    
    if (message != None):
        print(message)

def get_key() -> Optional[str]:
    if os.name == "nt":  # If the operating system is Windows
        if msvcrt.kbhit():  # Checks if a keypress is available
            return msvcrt.getch().decode("utf-8")  # Reads the keypress
    else:  # If the operating system is macOS or Linux
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            char = sys.stdin.read(1)
        except KeyboardInterrupt:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char
    
match_dir = ((1, 0), (0, -1), (-1, 0), (0, 1))
def find_matches(x: int, y: int) -> list:
    global matrix
    global match_dir

    base = matrix[y][x]
    x_list = [(x, y)]
    y_list = [(x, y)]

    for dir in range(4):
        xx = x
        yy = y

        while True:
            xx += match_dir[dir][0]
            yy += match_dir[dir][1]

            if not (yy in matrix and xx in matrix[yy] and matrix[yy][xx] == base):
                break
            
            if dir % 2 == 0:
                x_list.append((xx, yy))
            else:
                y_list.append((xx, yy))

    if len(x_list) >= len(y_list):
        return x_list
    else:
        return y_list
    
def clear_board(batch: tuple):
    global score
    global clearing

    clearing = True

    for i in batch:
        score += 50
        matrix[i[1]][i[0]] = "🌀"

    
def get_random_fruit() -> "str":
    return fruits[ random.randint(0, len(fruits) - 1) ]

for y in range(grid_y):
    matrix[y] = {}
    for x in range(grid_x):
        matrix[y][x] = get_random_fruit()
        while len(find_matches(x, y)) > 2:
            matrix[y][x] = get_random_fruit()

def display():
    global clear_x
    global clear_y
    global matrix
    global score
    global clearing
    global refresh

    while True:
        if refresh:
            display_text = ""
            cleared = False

            for i in range(3):
                for y in matrix:
                    y = grid_y - y - 1
                    for x in matrix[y]:
                        newText = matrix[y][x]

                        if i == 0:
                            if newText != "🌀":
                                matches = find_matches(x, y)
                                if len(matches) > 2:
                                    clear_board(matches)
                        elif i == 1:
                            if newText == "🌀":
                                if y == grid_y - 1:  
                                    matrix[y][x] = get_random_fruit()
                                else:
                                    matrix[y][x] = matrix[y + 1][x]
                                    matrix[y + 1][x] = "🌀"

                                cleared = True
                        elif i == 2:
                            if x == prev_x and y == prev_y:
                                newText = f"{GREEN}[{newText}]{RESET}"
                            elif x == select_x and y == select_y:
                                newText = f"{YELLOW}[{newText}]{RESET}"
                            else:
                                newText = f" {newText} "
                        
                            display_text += newText
                    if i == 2:
                        display_text += "\n"

                if i == 2:
                    display_text += f"score: {score}p"
                    update_terminal(display_text)

                    if not cleared:
                        clearing = False
                    else:
                        time.sleep(0.05)
            
        time.sleep(1/30)
        
def inputs():
    global matrix
    global select_x
    global select_y
    global prev_x
    global prev_y
    global refresh
    global clearing

    while True:
        key = get_key()
        if key == "w":
            select_y += 1
        elif key == "a":
            select_x -= 1
        elif key == "s":
            select_y -= 1
        elif key == "d":
            select_x += 1
        elif key == "e":
            if clearing:
                continue

            if prev_x == None:
                prev_x = select_x
                prev_y = select_y
            else:
                if (select_x - prev_x == 0) != (select_y - prev_y == 0):
                    select = matrix[select_y][select_x]
                    prev = matrix[prev_y][prev_x]

                    matrix[select_y][select_x] = prev
                    matrix[prev_y][prev_x] = select

                    select_matches = find_matches(select_x, select_y)
                    prev_matches = find_matches(prev_x, prev_y)

                    if len(select_matches) > 2:
                        clear_board(select_matches)
                    
                    if len(prev_matches) > 2:
                        clear_board(prev_matches)
                        

                prev_x, prev_y = None, None

        select_x = max(0, (prev_x or 0) - 1, min(select_x, (prev_x or grid_x) + 1, grid_x - 1))
        select_y = max(0, (prev_y or 0) - 1, min(select_y, (prev_y or grid_y) + 1, grid_y - 1))
        
display_thread = threading.Thread(target=display)
inputs_thread = threading.Thread(target=inputs)

display_thread.start()
inputs_thread.start()