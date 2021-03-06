from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from math import sqrt
import re

class Tile:
    def __init__(self, tile):
        self.tile = tile
        self.color = Tile.get_rgb(tile.get_attribute("colorid"))
        self.loca, self.id = self.__get_loca_and_id()
        
    def click(self):
        self.tile.click()

    def __get_loca_and_id(self):
        tile_id = self.tile.get_attribute('id')
        row = int(tile_id[-2]) if tile_id[-2] != '-' else 0
        col = int(tile_id[-1])
        return (row, col), tile_id

    @classmethod
    def get_rgb(self, rgb):
        '''
        takes CSS string of the rgb value and returns it as a tuple
        '''
        rgb = re.search(r'rgb\((?P<red>\d{,3}), (?P<green>\d{,3}), (?P<blue>\d{,3})\)', rgb)
        return (int(rgb.group('red')), int(rgb.group('green')), int(rgb.group('blue')))

    def __str__(self) -> str:
        return f'{self.loca}'

    def __repr__(self) -> str:
        return f'{self.loca}'

    def __gt__(self, other):
        tup_to_num = lambda tup: int(str(tup[0])+str(tup[1]))
        return  tup_to_num(self.loca) > tup_to_num(other.loca)

    def __ge__(self, other):
        tup_to_num = lambda tup: int(str(tup[0])+str(tup[1]))
        return  tup_to_num(self.loca) >= tup_to_num(other.loca)

    def __lt__(self, other):
        tup_to_num = lambda tup: int(str(tup[0])+str(tup[1]))
        return  tup_to_num(self.loca) < tup_to_num(other.loca)

    def __le__(self, other):
        tup_to_num = lambda tup: int(str(tup[0])+str(tup[1]))
        return  tup_to_num(self.loca) <= tup_to_num(other.loca)


class Chroma:
    def __init__(self) -> None:
        self.url = 'https://jessicaup.github.io/dull/'
        self.driver =  webdriver.Firefox()
        self.board = []
        self.max_moves = 0
        self.paths = []
        self.start = {
            "color": (None, None, None),
            "loca": (None, None)
        }
        self.target = {
            "color": (None, None, None),
            "loca": (None, None)
        }


    def grab_target_and_start_colors(self):
        self.start['color'] = Tile.get_rgb(self.driver.find_element(By.ID, 'current-color').get_attribute('style'))

        self.target['color'] = Tile.get_rgb(self.driver.find_element(By.TAG_NAME, 'body').get_attribute('style'))
        

    def find_start(self):
        if self.start['color'][0] == None:
            self.grab_target_and_start_colors()

        for row in range(len(self.board)):
            for col in range(len(self.board)):
                tile = self.board[row][col]
                if tile.color == self.start['color']:
                    self.start['loca'] = tile.loca


    def find_target(self):
        try:
            star = self.driver.find_element(By.CLASS_NAME, 'star')
        except:
            star = None
        if star:
            parent_id = star.find_element(By.XPATH, './..').get_attribute('id')
            row = int(parent_id[-2]) if parent_id[-2] != '-' else 0
            col = int(parent_id[-1])
            self.target['loca'] = (row, col)

    def grab_board(self):
        def quickSort(arr: list) -> list:
            if len(arr) <= 0:
                return arr

            pivot = [arr[0]]
            left_wing = [x for x in arr[1:] if x < pivot[0]]
            right_wing = [y for y in arr[1:] if y >= pivot[0]]

            return quickSort(left_wing) + pivot + quickSort(right_wing)

        eles = self.driver.find_elements(By.CLASS_NAME, 'mix-tile')
        self.board, tiles, seen_tiles = [], [], set()

        for tile in eles:
            new_tile = Tile(tile)
            if new_tile.loca not in seen_tiles:
                seen_tiles.add(new_tile.loca)
                tiles.append(new_tile)

        tiles = quickSort(tiles)

        for _ in range(10):
            row = []
            for _ in range(10):
                row.append(tiles.pop(0))
            self.board.append(row)


    def get_max_moves(self):
        self.max_moves = int(self.driver.find_element(By.CLASS_NAME, 'dot').text)


    def start_and_clear_popup(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(2)
        self.driver.find_element(By.CLASS_NAME, 'close-button').click()


    def close(self):
        self.driver.close()


    def next_level(self, paths, idx):
        sleep(1)
        try:
            self.driver.find_element(By.CLASS_NAME, 'level-button').click()
        except:
            hearts = self.driver.find_element(By.CLASS_NAME, 'lives').text
            if int(hearts) <= 1:
                print('Chroma: Ah, I don\'t have many lives left, I\'ll stop here.')
                exit()
            print('Chroma: Hmm... I don\'t think that was the right path. I\'ll try again')
            idx += 1
            sleep(.5)
            self.driver.find_element(By.CLASS_NAME, 'dot').click()
            self.travel_path(self.paths[paths[idx]])
            print(f'Chroma: Trying path number {idx+1}')
            self.next_level(paths, idx)
        finally:
            sleep(.5)


    def complete_level_one(self):
        sleep(.5)
        self.driver.find_element(By.CLASS_NAME, 'arrow-icons').click()
        sleep(1)
        self.driver.find_element(By.CLASS_NAME, 'level-button').click()
        
    def travel_path(self, path):
        sleep(0.6)
        body = self.driver.find_element(By.TAG_NAME, 'body')
        old_tile = path[0]
        for tile in path[1:]:
            row, col = tile.loca[0] - old_tile.loca[0], tile.loca[1] - old_tile.loca[1]
            if row == -1:
                body.send_keys(Keys.UP)
            elif row == 1:
                body.send_keys(Keys.DOWN)
            elif col == 1:
                body.send_keys(Keys.RIGHT)
            elif col == -1:
                body.send_keys(Keys.LEFT)
            old_tile = tile
            sleep(0.1)


    def vaild_loca(self, row, col):
        if not 9 >= row >= 0:
            return False
        if not 9 >= col >= 0:
            return False
        return True


    def rgb_to_cymk(self, rgb):
        cyan, mage, yell = 255 - rgb[0], 255 - rgb[1], 255 - rgb[2]
        black = min(cyan, mage, yell)
        cyan, mage, yell = ((cyan - black)/(255-black)), ((mage - black)/(255-black)), ((yell - black)/(255-black))
        return ( cyan, mage, yell, black/255 )

    def cymk_to_rgb(self, cymk):
        rgb_helper = lambda color_idx: int((1.0 - (cymk[color_idx] * (1.0 - cymk[3]) + cymk[3])) * 255.0 + 0.5)
        red, green, blue = rgb_helper(0), rgb_helper(1), rgb_helper(2)
        return (red, green, blue)

    def mix_colors(self, color1, color2=None):
        if type(color1) != list and color2 != None:
            color1 = [color1, color2]

        cyan = mage = yell = black = 0
        for color in color1:
            color = self.rgb_to_cymk(color)
            cyan += color[0]
            mage += color[1]
            yell += color[2]
            black += color[3]
        cyan, mage, yell, black = cyan/len(color1), mage/len(color1), yell/len(color1), black/len(color1)
        return self.cymk_to_rgb((cyan, mage, yell, black))

    def path_color(self, path):
        colors = [color.color for color in path]
        return self.mix_colors(colors)


    def find_paths(self, loca=None, path=[]):
        loca = loca or self.start['loca']
        path = path or [self.board[loca[0]][loca[1]]]

        if loca == self.target['loca'] and len(path)-1 == self.max_moves:
            self.paths.append(path)
        if self.max_moves+1 <= len(path):
            return None

        for move in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            row, col =  loca[0]+move[0], loca[1]+move[1]
            if self.vaild_loca(row, col) and self.board[row][col] not in path:
                path.append(self.board[row][col])
                new_path = path.copy()
                posi_path = self.find_paths((row, col), new_path)
                if posi_path != None:
                    return posi_path
                else:
                    if len(path) > 1:
                        path.pop(-1)


    def get_best_paths(self):
        tr, tg, tb = self.target['color']
        colors = []
        for i, path in enumerate(self.paths):
            colors.append( (*self.path_color(path), i) )
            
        colors_diffs, best_paths = [], []
        for color in colors:
            r, g, b, idx = color
            diff = sqrt( (tr - r)**2 + (tg - g)**2 + (tb - b)**2 )
            colors_diffs.append((diff, color))

        while len(colors_diffs) > 0:
            b_path = min(colors_diffs)[1][3]
            best_paths.append(b_path)
            for idx, color_path in enumerate(colors_diffs):
                if color_path[1][3] == b_path:
                    colors_diffs.pop(idx)
                    break


        return best_paths


    def get_all_data(self):
        sleep(.1)
        self.grab_board()
        self.grab_target_and_start_colors()
        self.find_start()
        self.find_target()
        self.get_max_moves()
        self.paths = []
    
    def play(self, end_round):
        self.start_and_clear_popup()
        self.complete_level_one()
        for _ in range(end_round-1):
            sleep(1)
            self.get_all_data()
            self.find_paths()
            paths = self.get_best_paths()
            print(f'Chroma: Round {_+2} has {len(paths)} possible paths')
            self.travel_path(self.paths[paths[0]])
            self.next_level(paths, 0)
        print(f'Chroma: All done! I played {end_round} rounds!')


    def test(self):
        self.start_and_clear_popup()
        self.complete_level_one()

        self.get_all_data()
        self.find_paths()



if __name__ == '__main__':
    chroma = Chroma()
    chroma.play(50)
