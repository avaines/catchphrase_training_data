#!/bin/bash
# Theres something wonky about the image resizing i cant be bothered to figure out yet
# convert $1 -resize 732x564! $1

exclusion_file="catchphrase-bjss-block.png"

while IFS= read -r file_name; do
    echo "Resizing: $file_name"
    convert "$file_name" -resize 732x564! "$file_name"
done < <(find ./ -type f \( -name "*.jpeg" -o -name "*.png" \) -maxdepth 1 | grep -v "$exclusion_file")
