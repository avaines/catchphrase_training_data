import argparse
import cv2
import numpy as np
from PIL import Image
import os
import random



def divide_image(image):
    rows = np.split(image, 3)  # Split into 3 rows
    sections = []

    for row in rows:
        divided_row = np.hsplit(row, 3)  # Split each row into 3 sections
        sections.extend(divided_row)

    return sections


def apply_gaussian_blur(image, sections_to_blur, sections):
    blurred_image = image.copy()
    section_height, section_width, _ = sections[0].shape

    for section_idx in sections_to_blur:
        row_idx = section_idx // 3
        col_idx = section_idx % 3
        section = sections[row_idx][col_idx]
        blurred_section = cv2.GaussianBlur(section, (5, 5), 0)  # Apply Gaussian blur
        blurred_image[row_idx * section_height:(row_idx + 1) * section_height,
                      col_idx * section_width:(col_idx + 1) * section_width] = blurred_section

    return blurred_image


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



def blur(image_path, sections_to_transform):
    image = cv2.imread(image_path)
    sections = divide_image(image)
    filename = os.path.basename(image_path)

    blurred_image = apply_gaussian_blur(image, sections_to_transform, sections)

    transformed_filename = filename.replace('.', f'-{"-".join(map(str, sections_to_transform))}.')
    transformed_path = os.path.dirname(image_path) + "/gaussian/"

    if not os.path.exists(transformed_path):
        os.makedirs(transformed_path)

    blurred_path = transformed_path + transformed_filename
    cv2.imwrite(blurred_path, blurred_image)

    print(blurred_path)


def overlay_cards(image_path, overlay_image_path, sections_to_overlay):
    image = cv2.imread(image_path)
    sections = divide_image(image)
    filename = os.path.basename(image_path)

    overlaid_image = apply_overlay_cards(image, sections_to_overlay, overlay_image_path, sections)

    overlaid_filename = filename.replace('.', f'-{"-".join(map(str, sections_to_overlay))}.')
    overlaid_path = os.path.dirname(image_path) + "/overlaid/"

    if not os.path.exists(overlaid_path):
        os.makedirs(overlaid_path)

    overlaid_path = overlaid_path + overlaid_filename

    overlaid_image_pil = Image.fromarray(overlaid_image)
    overlaid_image_pil.save(overlaid_path)

    print(overlaid_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", help="Path to the input image")
    parser.add_argument("--card", "-c", help="Path to the input image for the catchphrase card used for the overlay")
    parser.add_argument("--number", "-n", help="Number of random images to generate", default=25)

    args = parser.parse_args()

    list_length = random.randint(1, 9)  # You can adjust the range of list lengths as needed
    numbers_range = list(range(9))  # Numbers 0 to 9

    for _ in range(args.number):
        list_length = random.randint(1, 6) # How many of the 9 sections of the image should be blured
        list_without_replacement = random.sample(numbers_range, list_length)
        list_without_replacement.sort()

        print("Generating image with the following sections blured:", str(list_without_replacement))
        blur(args.path, list_without_replacement)
        overlay_cards(args.path, args.card, list_without_replacement)
