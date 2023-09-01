import cv2
import json
import numpy as np
import os
import random
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image

app = Flask(__name__)

class gameState:
    def __init__(self):
        self.catchphrase_filename = "/static/base.png"
        self.ai_catchphrase_filename = self.catchphrase_filename

        self.ai_catchphrase_guess = ""
        self.ai_catchphrase_incorrect_guesses = []
        self.catchphrases = []
        self.catchphrases_dir = "./game/static/catchphrases/"
        self.current_catchphrase_name = ""
        self.current_catchphrase_value = 0
        self.current_image = ""
        self.hidden_boxes = []
        self.player_one_score = 0
        self.player_two_score = 0
        self.scores = [0, 0]

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
        self.current_catchphrase_name = os.path.basename(self.current_image).split(".")[0].replace("-"," ")


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

        # The AI should only have a black overlaid box
        ai_overlaid_image = self.apply_overlay_cards(image, self.hidden_boxes, "./game/static/catchphrase-black-block.jpg", sections)
        ai_overlaid_image_pil = Image.fromarray(ai_overlaid_image)
        ai_overlaid_image_pil.save("./game/static/ai-game-image.png")

        # Humans want something a bit more pretty
        overlaid_image = self.apply_overlay_cards(image, self.hidden_boxes, "./game/static/catchphrase-bjss-block.png", sections)
        overlaid_image_pil = Image.fromarray(overlaid_image)
        overlaid_image_pil.save("./game/static/game-image.png")

        self.catchphrase_filename = "/static/game-image.png"
        self.ai_catchphrase_filename="/static/ai-game-image.png"


def upload_blob_file(container_name: str, image_path: str):
    blob_sas_url=os.getenv("AZURE_BLOB_SAS_URL")
    blob_service_client = BlobServiceClient(blob_sas_url)

    container_client = blob_service_client.get_container_client(container=container_name)

    try:
        with open(file=image_path, mode="rb") as data:
            blob_client = container_client.upload_blob(name="ai-game-image.png", data=data, overwrite=True)

        return blob_client.url
    except:
        print("Unable to upload image, check 'AZURE_BLOB_SAS_URL' token environmental variable")


def call_catchphrase_ai_api(image_url):
    print(f"Calling catchphrase API with: {image_url}")
    incorrect_guesses = [x for x in Game.ai_catchphrase_incorrect_guesses if x]

    url = os.getenv("VISION_API_URL")
    params = {
        "imageUrl": image_url,
        "incorrectAnswers": ", ".join(incorrect_guesses),
        "code": os.getenv("VISION_API_KEY")
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        send_slack_message(message=f"AI Guess: :robot_face: {response.text}")
        return response.text

    else:
        send_slack_message(message=f"AI Guess: :robot_face: Request failed with status code: {response.status_code}")
        return ''


def send_slack_message(message):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    payload = {
            "message": message,
        }

    requests.post(webhook, json.dumps(payload))


# Routes
@app.route('/')
def index():
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value, ai_guess="") 


@app.route('/box_clicked/<box_number>')
def box_clicked(box_number):
    if int(box_number) in Game.hidden_boxes:
        Game.reveal([box_number])
        Game.current_catchphrase_value -= 100

        uploaded_ai_blob_url = upload_blob_file(container_name="game-images", image_path="./game/"+Game.ai_catchphrase_filename)

        Game.ai_catchphrase_incorrect_guesses.append(Game.ai_catchphrase_guess) # The current AI guess must be incorrect
        Game.ai_catchphrase_guess = call_catchphrase_ai_api(uploaded_ai_blob_url.split("?")[0])

    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value, ai_guess="")


@app.route('/award_player/<player_number>')
def award_player(player_number):
    Game.scores[int(player_number)] += Game.current_catchphrase_value
    Game.current_catchphrase_value = 0
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value, ai_guess="")


@app.route('/reveal')
def reveal():
    Game.reveal([0,1,2,3,4,5,6,7,8])
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value, ai_guess=Game.ai_catchphrase_guess)


@app.route('/ai_guess')
def ai_guess():
    return render_template("index.html", catchphrase_image=Game.catchphrase_filename, p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value, ai_guess=Game.ai_catchphrase_guess)


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
        Game.ai_catchphrase_incorrect_guesses = []

        send_slack_message(message=f" ")
        send_slack_message(message=f"Catchphrase: :speaker: {Game.current_catchphrase_name} :speaker:")

        return render_template("index.html", catchphrase_image="/static/base.png", p1_score=Game.scores[0], p2_score=Game.scores[1], catchprase_value=Game.current_catchphrase_value, ai_guess="")


if __name__ == '__main__':
    load_dotenv()
    Game = gameState()
    Game.selectCatchphrase()
    Game.current_catchphrase_value = 1000
    Game.hidden_boxes=[0,1,2,3,4,5,6,7,8]
    Game.ai_catchphrase_incorrect_guesses = []

    send_slack_message(message=f"Catchphrase: :speaker: {Game.current_catchphrase_name} :speaker:")

    print("Current Catchphrase is:", Game.current_image)
    app.run(debug=True, port=80)
