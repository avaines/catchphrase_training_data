from flask import Flask, render_template, request, jsonify
from PIL import Image
import cv2
import numpy as np
import os

app = Flask(__name__)

# Define a dictionary to map box numbers to image paths
box_image_mapping = {
    0: 'image0.jpg',
    1: 'image1.jpg',
    2: 'image2.jpg',
    # ... add more mappings as needed
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/box_clicked', methods=['POST'])
def box_clicked():
    box_number = int(request.form['box_number'])

    clicked_boxes.pop(box_number)

    overlay_cards(current_image, "static/catchphrase-bjss-block.png", clicked_boxes)



    image_path = box_image_mapping.get(box_number, 'default.jpg')
    return jsonify({'image_path': image_path})



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
        section = sections[row_idx][col_idx]

        resized_replacement = replacement_image.resize((section_width, section_height))  # Resize replacement image

        replaced_image[row_idx * section_height:(row_idx + 1) * section_height,
                      col_idx * section_width:(col_idx + 1) * section_width] = resized_replacement

    return replaced_image


def overlay_cards(image_path, overlay_image_path, sections_to_overlay):
    image = cv2.imread(image_path)
    sections = divide_image(image)
    filename = os.path.basename(image_path)

    overlaid_image = apply_overlay_cards(image, sections_to_overlay, overlay_image_path, sections)

    overlaid_filename = filename.replace('.', f'-{"-".join(map(str, sections_to_overlay))}.')
    overlaid_path = os.path.dirname(image_path) + "/overlaid/" + filename.split(".")[0] + "/"

    if not os.path.exists(overlaid_path):
        os.makedirs(overlaid_path)

    overlaid_path = overlaid_path + overlaid_filename

    overlaid_image_pil = Image.fromarray(overlaid_image)
    overlaid_image_pil.save(overlaid_path)

    print(overlaid_path)



if __name__ == '__main__':
    clicked_boxes = [0,1,2,3,4,5,6,7,8]
    current_image = "./static/scapegoat.jpeg"
    app.run(debug=True, port=5001)
