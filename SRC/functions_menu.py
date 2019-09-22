import os
import time
from functions_filter import get_address


def clear():
    '''
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
    '''
    os.system('clear')


def display_M1():
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    time.sleep(0.5)
    print('''
    PLEASE FILL THIS FORM:
    -----------------------------------------------------------------------
    | 1.- What kind of companies do you want around yours?:               |
    -----------------------------------------------------------------------
    '''
          )


def display_M2():
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
    | 2.- What amount of money should they have raised?:                  |
    -----------------------------------------------------------------------
    '''
          )


def display_M3():
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
    | 3.- Name one restaurant/café that you would like close to you:      |
    -----------------------------------------------------------------------
    '''
          )


def display_M4():
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
    | 4.- Name one service that you would like close to you:              |
    -----------------------------------------------------------------------
    '''
          )


def display_M5():
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
    | 4.- Which of the following events would you want close to you?:     |
    -----------------------------------------------------------------------
    -----------------------------------------------------------------------
    | tech | health-wellness | sports-fitness | education | photography | 
    | music | film | games-sci-fi |  arts-culture | fashion-beauty | 
    | social | career-business |
    -----------------------------------------------------------------------
    '''
          )


def display_M6(hostelry, service, cat_events):
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
      4.- Please rank from 1 (min) to 4 (max) the criteria to choose your 
          perfect location, separated by commas:                                                       
             - Companies around you                                       
             - {} around you                                              
             - {}s around you                                             
             - {} events around you                                       
    -----------------------------------------------------------------------
    '''.format(hostelry.title(), service.title(), cat_events.title()))


def display_M7():
    clear()
    print(
        '''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
    |         WE ARE CALCULATING TO FIND YOUR PERFECT LOCATION.....       |
    |                         PLEASE AWAIT.....                           |
    -----------------------------------------------------------------------
    '''
          )


def display_M8(coords):
    clear()
    print('''
    -----------------------------------------------------------------------
    -              FIND THE PERFECT LOCATION FOR YOUR COMPANY             -
    -----------------------------------------------------------------------
    ''')
    print('''
    -----------------------------------------------------------------------
               YOUR PERFECT LOCATION IS : {}       
                       {}                          
    -----------------------------------------------------------------------
    '''.format(coords, get_address(coords[1], coords[0])))
