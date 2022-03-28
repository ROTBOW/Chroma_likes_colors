from PIL import ImageGrab, ImageOps
import time
from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Tile:
    def __init__(self, tile):
        self.tile = tile

    def __str__(self) -> str:
        return f'{self.tile.get_attribute("colorid")}'

    def __repr__(self) -> str:
        return f'{self.tile.get_attribute("colorid")}'


class Chroma:
    def __init__(self) -> None:
        self.url = 'https://jessicaup.github.io/dull/'
        self.driver =  webdriver.Firefox()
        self.board = []


    def grab_board(self):
        tiles = self.driver.find_elements(By.CLASS_NAME, 'mix-tile')
        # for tile in tiles:
        #     print(tile.get_attribute('colorid'))
        # print(len(tiles))
        for _ in range(10):
            row = []
            for i in range(10):
                row.append(Tile(tiles.pop(0)))
            self.board.append(row)


    def clear_popup(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(2)
        self.driver.find_element(By.CLASS_NAME, 'close-button').click()


    def play(self, end_round):
        self.clear_popup()
        self.grab_board()
        print(self.board)




chroma = Chroma()

chroma.play(5)
    