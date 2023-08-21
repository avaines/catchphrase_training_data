from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import cv2
import numpy as np
import os
import random

app = Flask(__name__)

class gameState:
    def __init__(self):
        self.hidden_boxes = []
        self.catchphrase_filename = "/static/base.png"
        self.catchphrases_dir = "./game/static/catchphrases/"
        self.catchphrases = []
        self.scores = [0, 0]
        self.current_image = ""
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
        self.hidden_boxes = [0,1,2,3,4,5,6,7,8]
        self.catchphrase_filename = "/static/base.png"


    def apply_overlay_cards(self, image, sections_to_replace, replacement_image_path, sections):
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


    def divide_image(self, image):
        rows = np.split(image, 3)  # Split into 3 rows
        sections = []

        for row in rows:
            divided_row = np.hsplit(row, 3)  # Split each row into 3 sections
            sections.extend(divided_row)

        return sections


    def reveal(self, clicked_boxes: list):
        for clicked_box in clicked_boxes:
            if int(clicked_box) in self.hidden_boxes:
                self.hidden_boxes.remove(int(clicked_box))

        image = cv2.imread(self.current_image)
        sections = self.divide_image(image)

        overlaid_image = self.apply_overlay_cards(image, self.hidden_boxes, "./game/static/catchphrase-bjss-block.png", sections)

        overlaid_image_pil = Image.fromarray(overlaid_image)
        overlaid_image_pil.save("./game/static/game-image.png")
        self.catchphrase_filename = "/static/game-image.png"


@app.route('/')
def index():
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value)


@app.route('/box_clicked/<box_number>')
def box_clicked(box_number):
    Game.reveal([box_number])
    Game.current_catchphrase_value -= 100
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value)


@app.route('/award_player/<player_number>')
def award_player(player_number):
    Game.scores[int(player_number)] += Game.current_catchphrase_value
    Game.current_catchphrase_value = 0


    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value)


@app.route('/reveal')
def reveal():
    Game.reveal([0,1,2,3,4,5,6,7,8])
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value)


@app.route('/newgame')
def newgame():
    if len(Game.catchphrases) < 1:
        print("No more catchphrases")
        return redirect("/", code=302)
    else:
        print("Catchphrases left:", len(Game.catchphrases))
        Game.selectCatchphrase()
        Game.current_catchphrase_value = 1000
        Game.hidden_boxes=[0,1,2,3,4,5,6,7,8]

        return render_template("index.html", catchphrase_image="/static/base.png", p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value)

if __name__ == '__main__':
    Game = gameState()
    Game.selectCatchphrase()
    print("Current Catchphrase is:", Game.current_image)
    app.run(debug=True, port=5001)

