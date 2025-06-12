# コンソール用色付き文字出力
import os

os.system('')

NORMAL = '\033[0m'
INFO_BLUE = '\033[94m'
INFO_GREEN = '\033[92m'
WARN = '\033[93m'
ERR = '\033[91m'

BOLD = '\033[1m'

_END = '\033[0m'

def text(text, pattern=()):
    colored_text = ""
    for style in pattern:
        colored_text += style

    colored_text += text
    colored_text += _END
    print(colored_text)

Normal = [
    NORMAL,
]
Log = [
    INFO_GREEN,
]
Data = [
    INFO_BLUE,
]
Warn = [
    BOLD,
    WARN,
]
Error = [
    BOLD,
    ERR,
]