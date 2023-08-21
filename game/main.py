from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import cv2
import numpy as np
import os
import random

app = Flask(__name__)

class gameState:
    def __init__(self):
        self.clicked_boxes = []
        self.catchphrase_filename = "./static/" + "base.png"
        self.catchphrases_dir = "./game/static/catchphrases/"
        self.catchphrases = []
        self.player_one_score = 0
        self.player_two_score = 0
        self.current_catchphrase_value = 0

        for file in os.listdir(self.catchphrases_dir):
            if file.endswith('.png'):
                self.catchphrases.append(file)

    def selectCatchphrase(self):
        catchphrase_num = random.randint(0, len(self.catchphrases)-1)
        self.current_image = self.catchphrases_dir + self.catchphrases[catchphrase_num]
        del self.catchphrases[catchphrase_num]
        self.current_catchphrase_value = 1000
        self.clicked_boxes = [0,1,2,3,4,5,6,7,8]

@app.route('/')
def index():
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.player_one_score, p2_score=Game.player_two_score, catchprase_value=Game.current_catchphrase_value)


@app.route('/box_clicked/<box_number>')
def box_clicked(box_number):
    try:
        Game.clicked_boxes.remove(int(box_number))
        Game.current_catchphrase_value -= 100
    except ValueError:
        pass

    image = cv2.imread(Game.current_image)
    sections = divide_image(image)

    overlaid_image = apply_overlay_cards(image, Game.clicked_boxes, "./game/static/catchphrase-bjss-block.png", sections)

    overlaid_image_pil = Image.fromarray(overlaid_image)
    overlaid_image_pil.save("./game/static/game-image.png")
    catchphrase_filename = "/static/game-image.png"

    return render_template("index.html", catchphrase_image=catchphrase_filename, p1_score=Game.player_one_score, p2_score=Game.player_two_score, catchprase_value=Game.current_catchphrase_value)


def divide_image(image):
    rows = np.split(image, 3)  # Split into 3 rows
    sections = []

    for row in rows:
        divided_row = np.hsplit(row, 3)  # Split each row into 3 sections
        sections.extend(divided_row)

    return sections


def apply_overlay_cards(image, sections_to_replace, replacement_image_path, sections):
    replaced_image = image.copy()
    replacement_image = Image.open(replacement_image_path)
    section_height, section_width, _ = sections[0].shape

    for section_idx in sections_to_replace:
        row_idx = section_idx // 3
        col_idx = section_idx % 3

        resized_replacement = replacement_image.resize((section_width, section_height))  # Resize replacement image

        replaced_image[row_idx * section_height:(row_idx + 1) * section_height,
                      col_idx * section_width:(col_idx + 1) * section_width] = resized_replacement

    return replaced_image


if __name__ == '__main__':
    Game = gameState()
    Game.selectCatchphrase()

    app.run(debug=True, port=5001)

