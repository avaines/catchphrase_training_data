from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import cv2
import numpy as np
import os
import random

app = Flask(__name__)

class gameState:
    def __init__(self):
        catchphrases_dir = "./game/static/catchphrases/"
        catchphrases = []
        player_one_score = 0
        player_two_score = 0
        current_catchphrase_value = 1000

        for file in os.listdir(catchphrases_dir):
            if file.endswith('.png'):
                catchphrases.append(file)
        catchphrase_num = random.randint(0, len(catchphrases)-1)
        current_image = catchphrases_dir + catchphrases[catchphrase_num]


@app.route('/')
def index():
    return render_template("index.html", catchphrase_image=catchphrase_filename)


@app.route('/box_clicked/<box_number>')
def box_clicked(box_number):
    try:
        clicked_boxes.remove(int(box_number))
    except ValueError:
        pass

    image = cv2.imread(current_image)
    sections = divide_image(image)

    overlaid_image = apply_overlay_cards(image, clicked_boxes, "./game/static/catchphrase-bjss-block.png", sections)

    overlaid_image_pil = Image.fromarray(overlaid_image)
    overlaid_image_pil.save("./game/static/game-image.png")
    catchphrase_filename = "./static/game-image.png"

    return render_template("index.html", catchphrase_image="../" + catchphrase_filename, p1_score=player_one_score, p2_score=player_two_score, catchprase_value=current_catchphrase_value)


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
    clicked_boxes = [0,1,2,3,4,5,6,7,8]
    catchphrase_filename = "./static/" + "base.png"
    

    app.run(debug=True)

