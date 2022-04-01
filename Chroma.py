from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
import re

class Tile:
    def __init__(self, tile):
        self.tile = tile
        self.color = Tile.get_rgb(tile.get_attribute("colorid"))
        self.loca = self.__get_loca()

    def click(self):
        self.tile.click()

    def __get_loca(self):
        tile_id = self.tile.get_attribute('id')
        row = int(tile_id[-2]) if tile_id[-2] != '-' else 0
        col = int(tile_id[-1])
        return (row, col)

    @classmethod
    def get_rgb(self, rgb):
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
        tiles = []
        seen_tiles = set()
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


    def next_level(self, second_attempt=False):
        self.driver.implicitly_wait(2)
        try:
            if not second_attempt:
                self.driver.find_element(By.CLASS_NAME, 'level-button').click()
        except:
            print('something went wrong, trying again...')
            self.next_level(True)


    def complete_level_one(self):
        sleep(.5)
        self.driver.find_element(By.CLASS_NAME, 'arrow-icons').click()
        self.next_level()

    def step(self, move, row, col):
        if move == 'up':
            row -= 1
        if move == 'down':
            row += 1
        if move == 'left':
            col -= 1
        if move == 'right':
            col += 1
        self.board[row][col].click()
        

    def travel_path(self, path):
        row, col = self.start['loca'][0], self.start['loca'][1]
        for move in path:
            self.step(move, row, col)
            sleep(0.8)

    def vaild_loca(self, row, col):
        if not 9 >= row >= 0:
            return False
        if not 9 >= col >= 0:
            return False
        return True


    def mix_colors(self, color1, color2):
        new_color = [None, None, None]
        for i in range(3):
            new_color[i] = int((color1[i] + color2[i]) / 2) 
        return tuple(new_color)

    def find_path(self, loca=None, color=None, path=[]):
        if color == self.target['color']:
            return path
        if loca == self.target['loca']:
            print('color', color)
            self.paths.append(path)
        if self.max_moves+1 <= len(path):
            return None

        loca = loca or self.start['loca']
        color = color or self.start['color']
        path = path or [self.board[loca[0]][loca[1]]]

        for move in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            row, col =  loca[0]+move[0], loca[1]+move[1]
            if self.vaild_loca(row, col) and self.board[row][col] not in path:
                print(path)
                path.append(self.board[row][col])
                new_path = path.copy()
                posi_path = self.find_path((row, col), self.mix_colors(color, self.board[row][col].color), new_path)
                if posi_path != None:
                    return posi_path
                else:
                    if len(path) > 1:
                        path.pop(-1)


    def get_all_data(self):
        sleep(.5)
        self.grab_board()
        self.grab_target_and_start_colors()
        self.find_start()
        self.find_target()
        self.get_max_moves()
    
    def play(self, end_round):
        self.start_and_clear_popup()
        self.complete_level_one()
        for _ in range(end_round-1):
            self.get_all_data()
            path = self.find_path()
            self.travel_path(path)
            self.next_level()


    def test(self):
        self.start_and_clear_popup()
        self.complete_level_one()

        self.get_all_data()
        path = self.find_path()
        print('path', path)
        print('paths', self.paths)
        print('target color', self.target['color'])
        # print(self.paths)
        # self.find_target()
        # print(self.target['loca'])
        # print(self.start['loca'])
        # print(self.board)
        # self.close()

        # (0, 230, 230)
        # (0, 204, 204)
        # (24, 153, 178)




if __name__ == '__main__':
    chroma = Chroma()
    chroma.test()
