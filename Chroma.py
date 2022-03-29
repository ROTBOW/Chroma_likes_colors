from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import re

class Tile:
    def __init__(self, tile):
        self.tile = tile

    def __str__(self) -> str:
        return f'{self.tile.get_attribute("colorid")}'

    def __repr__(self) -> str:
        return f'{self.tile.get_attribute("colorid")}'

    def color(self):
        return Tile.get_rgb(self.tile.get_attribute("colorid"))

    def click(self):
        self.tile.click()

    @classmethod
    def get_rgb(self, rgb):
        rgb = re.search(r'rgb\((?P<red>\d{,3}), (?P<green>\d{,3}), (?P<blue>\d{,3})\)', rgb)
        return (int(rgb.group('red')), int(rgb.group('green')), int(rgb.group('blue')))


class Chroma:
    def __init__(self) -> None:
        self.url = 'https://jessicaup.github.io/dull/'
        self.driver =  webdriver.Firefox()
        self.board = []
        self.turns = 0
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
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                tile = self.board[row][col]
                if tile.color() == self.start['color']:
                    self.start['loca'] = (row, col)


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
        tiles = self.driver.find_elements(By.CLASS_NAME, 'mix-tile')
        for _ in range(10):
            row = []
            for _ in range(10):
                row.append(Tile(tiles.pop(0)))
            self.board.append(row)


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


    def ask_for_move(self):
        print('please enter the answer for the first level')
        while True:
            move = input('-> ')
            if move in ['up', 'down', 'left', 'right']:
                break
        if self.start['loca'][0] == None:
            self.find_start()
        row, col = self.start['loca'][0], self.start['loca'][1]
        if move == 'up':
            row -= 1
        if move == 'down':
            row += 1
        if move == 'left':
            col -= 1
        if move == 'right':
            col += 1
        self.board[row][col].click()
        self.next_level()
        
    

    def play(self, end_round):
        self.start_and_clear_popup()
        self.grab_board()
        self.grab_target_and_start_colors()
        self.find_start()
        self.ask_for_move()
        self.find_target()
        print(self.target['loca'])
        # print(self.start['loca'])
        # print(self.board)
        # self.close()




if __name__ == '__main__':
    chroma = Chroma()
    chroma.play(5)
