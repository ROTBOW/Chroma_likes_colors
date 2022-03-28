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

    @classmethod
    def get_rgb(self, rgb):
        rgb = re.search(r'rgb\((?P<red>\d{,3}), (?P<green>\d{,3}), (?P<blue>\d{,3})\)', rgb)
        return (int(rgb.group('red')), int(rgb.group('green')), int(rgb.group('blue')))


class Chroma:
    def __init__(self) -> None:
        self.url = 'https://jessicaup.github.io/dull/'
        self.driver =  webdriver.Firefox()
        self.board = []
        self.target_color = None
        self.current_color = None
        self.start_loca = [None, None]


    def grab_target_and_currecnt(self):
        self.current_color = Tile.get_rgb(self.driver.find_element(By.ID, 'current-color').get_attribute('style'))

        self.target_color = Tile.get_rgb(self.driver.find_element(By.TAG_NAME, 'body').get_attribute('style'))
        

    def find_start_loca(self):
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                if self.board[row][col].color() == self.current_color:
                    self.start_loca = (row, col)


    def grab_board(self):
        tiles = self.driver.find_elements(By.CLASS_NAME, 'mix-tile')
        for _ in range(10):
            row = []
            for _ in range(10):
                row.append(Tile(tiles.pop(0)))
            self.board.append(row)


    def clear_popup(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(2)
        self.driver.find_element(By.CLASS_NAME, 'close-button').click()

    def close(self):
        self.driver.close()


    def play(self, end_round):
        self.clear_popup()
        self.grab_board()
        self.grab_target_and_currecnt()
        self.find_start_loca()
        print(self.start_loca)
        # print('cur', self.current_color)
        # print('tar', self.target_color)
        # print(self.board)
        # self.close()




if __name__ == '__main__':
    chroma = Chroma()
    chroma.play(5)
