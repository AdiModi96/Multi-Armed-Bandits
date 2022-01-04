import os
from os import system

def clear_terminal():
    if os.name == 'nt':
        system('cls')
    elif os.name == 'posix':
        system('clear')
    else:
        print('Unknown operating system')