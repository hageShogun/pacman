class Map:
    def __init__(self, map_file=None):
        self.init_map = None
        if map_file is not None:
            self.load_map(map_file)

    def load_map(self, map_file):
        map_data = []
        with open(map_file) as fin:
            while True:
                line = fin.readline()
                if not line:
                    break
                line = [int(x) for x in list(line.rstrip())]
                map_data.append(line)
        self.init_map = map_data
        return self.init_map

    def dump(self):
        for rows in self.init_map:
            for d in rows:
                print(d, end='')
            print('')


if __name__ == '__main__':
    import sys
    game_map = Map(sys.argv[1])
    game_map.dump()
    
    
