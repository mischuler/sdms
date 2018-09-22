#`/usr/bin/python

import sys
import inspect
import datetime

# LEVEL is defined as
# D for DEBUG
# I for INFO
# W for WARN
# E for ERROR

def log(CAT, message):

    # Set directory
    direct = '/Assets/logs/'
    logf = 'testlog.txt'

    # Set debug level
    DEBUG = False

    # Set categories
    C = {
        'D' :'DEBUG'
        , 'I' : 'INFO'
        , 'W' : 'WARN'
        , 'E' : 'ERROR'
        }
    
    # Performs lookup and sets category to info if programmers make an error
    try:
        category = C[CAT]
    except KeyError:
        category = 'INFO'

    # Get the file that called the log
    # and the method that called the log
    stack =  inspect.stack()[1]
    caller = stack[1]
    method =  stack[3]

    # Set the log with DATE, CATEGORY, CALLER, METHOD, and passed in MESSAGE
    line = '[%s][%s][%s][%s]\t%s\n' %(unicode(datetime.datetime.now()), category, caller, method, message)
    
    # Write the file if it's not a debug statement or debug is turned on 
    if CAT != 'D' or DEBUG:
        with open(direct+logf,'a') as logfile:
            logfile.write(line)


def main(args):
    
    log(args[1],args[2])


if __name__ == "__main__":
    
    main(sys.argv)
