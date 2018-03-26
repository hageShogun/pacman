END = '\033[0m'
colors = {'BLACK': '\033[30m',
          'RED': '\033[31m',
          'GREEN': '\033[32m',
          'YELLOW': '\033[33m',
          'BLUE': '\033[34m',
          'PURPLE': '\033[35m',
          'CYAN': '\033[36m',
          'WHITE': '\033[37m',
          'BOLD': '\033[38m'}


def coloring(str, color):
    if color in colors:
        return colors[color] + str + END
    else:
        return colors['RED'] + 'Given color does NOT exist.' + END


if __name__ == '__main__':
    s = 'hello'
    print(coloring(s, 'RED'))
    print(coloring(s, 'BLUE'))
    print(coloring(s, 'GRAY'))    
