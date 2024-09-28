import os

PATH = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(PATH,'tmp')
VENTOY_MNT_PATH = os.path.join('/','mnt','ventoy')
MIRRORS_JSON = os.path.join(PATH, 'mirrors.json')
ARCH = 'x86_64'

# ANSI Escape Sequences (for colored terminal output)
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
ORANGE = '\033[33m'
BLUE = '\033[34m'
PURPLE = '\033[35m'
CYAN = '\033[36m'
LIGHTGREY = '\033[37m'
DARKGREY = '\033[90m'
LIGHTRED = '\033[91m'
LIGHTGREEN = '\033[92m'
YELLOW = '\033[93m'
LIGHTBLUE = '\033[94m'
PINK = '\033[95m'
LIGHTCYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[01m'