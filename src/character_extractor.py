import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

CHARACTER_VERSIONS = [
    "Trouble Brewing",
    "Sects & Violets",
    "Bad Moon Rising",
    "Experimental Characters",
]

# Add Fabled functionality
CHARACTER_TYPES = ["Townsfolk", "Outsiders", "Minions", "Demons"]
BASE_URL = "https://wiki.bloodontheclocktower.com/Category:"


def get_soup_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=1)
            return BeautifulSoup(response.text, "html.parser")
        except requests.Timeout:
            print(f"Timeout occurred. Retrying... ({attempt + 1}/{max_retries})")
            sleep(2)
    print(f"Failed to fetch data for {url} after {max_retries} retries.")
    exit(0)


def get_all_soup():
    combined_html = ""

    for character_type in CHARACTER_TYPES:
        full_url = BASE_URL + character_type
        soup = get_soup_with_retry(full_url)
        if soup:
            combined_html += str(soup)
        else:
            print(
                f"Failed to get soup from my query to {full_url} - got this instead: {soup}"
            )

    return BeautifulSoup(combined_html, "html.parser")


def extract_version_and_type(soup):
    categories_links = soup.find_all(
        "a", href=lambda href: href and href.startswith("/Category:")
    )

    [char_version, char_type] = [cat_link.text for cat_link in categories_links]

    if char_version not in CHARACTER_VERSIONS:
        raise ValueError(f"Unknown character version {char_version}")

    if char_type not in CHARACTER_TYPES:
        raise ValueError(f"Unknown character type {char_type}")

    return char_version, char_type


def extract_ability_data(soup):
    ability_section = soup.find("span", {"id": "Summary"})

    char_ability = (
        ability_section.find_next("p").text.strip().replace('"', "")
        if ability_section
        else None
    )
    char_setup_modifier_match = re.search(
        r"\[([^]]*)", str(ability_section.find_next("p").text)
    )
    char_setup_modifier = (
        char_setup_modifier_match.group(1) if char_setup_modifier_match else None
    )

    return char_ability, char_setup_modifier


def fetch_character_info(character_url):
    soup = get_soup_with_retry(character_url)

    char_version, char_type = extract_version_and_type(soup)

    char_ability, char_setup_modifier = extract_ability_data(soup)

    return {
        "Version": char_version,
        "Type": char_type,
        "Ability": char_ability,
        "Setup Modifier": char_setup_modifier,
    }


def fetch_characters_info(current_character_info):
    soup = get_all_soup()

    char_info = {}

    character_links = soup.select("div.mw-category-generated ul li a[href]")

    for link in character_links:
        character_name = link.text
        if character_name not in current_character_info:
            print(f"Writing {character_name}")
            character_url = "https://wiki.bloodontheclocktower.com" + link["href"]
            char_info[character_name] = fetch_character_info(character_url)
        else:
            print(f"Skipped {character_name}")

    return char_info


def print_characters_info(char_info):
    for char_name, data in char_info.items():
        print(f"\nName: {char_name}")
        print(f"Version: {data['Version']}")
        print(f"Type: {data['Type']}")
        print(f"Ability: {data['Ability']}")
        if data["Setup Modifier"] is not None:
            print(f"Setup Modifier: [{data['Setup Modifier']}]\n")


def merge_data_to_file(data, filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            existing_data = json.load(file)

        existing_data.update(data)

        sorted_data = dict(sorted(existing_data.items()))

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(sorted_data, file, indent=4)

    except IOError as misc_error:
        print(f"Error merging and sorting data to file {filename}: {misc_error}")


def read_data_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data

    except IOError as misc_error:
        print(f"Error reading from file {filename}: {misc_error}")
        return None


def update_character_data(character_file_link):
    current_characters_info = read_data_from_file(character_file_link)
    new_characters_info = fetch_characters_info(current_characters_info)
    print_characters_info(new_characters_info)
    merge_data_to_file(new_characters_info, character_file_link)


CHARACTER_FILE_LINK = ".\\character_data\\character_data.json"

update_character_data(CHARACTER_FILE_LINK)
