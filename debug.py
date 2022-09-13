from datetime import datetime

# DEBUG stuff
DEBUG = True

def print_debug(message):
    if DEBUG:
        print(f"[{str(datetime.now()).split(' ')[1]} - DEBUG] {message}")
    return