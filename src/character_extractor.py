import json
import re
import requests
from bs4 import BeautifulSoup

character_versions = [
    "Trouble Brewing",
    "Sects & Violets",
    "Bad Moon Rising",
    "Experimental Characters",
]
character_types = ["Townsfolk", "Outsider", "Minion", "Demon", "Fabled"]


def gimmie_soup(timeout = 2):
    url = "https://wiki.bloodontheclocktower.com/Category:Townsfolk"
    response = requests.get(url, timeout=timeout, verify=False)
    return BeautifulSoup(response.text, "html.parser")


def extract_version_and_type(soup):
    categories_links = soup.find_all('a', href=lambda href: href and href.startswith('/Category:'))

    [char_version, char_type] = [cat_link.text for cat_link in categories_links]

    if char_version not in character_versions:
        raise ValueError(f"Unknown character version {char_version}")

    if char_type not in character_types:
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
    char_setup_modifier = (char_setup_modifier_match.group(
        1) if char_setup_modifier_match else None)

    return char_ability, char_setup_modifier


def fetch_character_info(character_url):
    response = requests.get(character_url, timeout=1)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    char_version, char_type = extract_version_and_type(
        soup)

    char_ability, char_setup_modifier = extract_ability_data(soup)

    return {
        "Version": char_version,
        "Type": char_type,
        "Ability": char_ability,
        "Setup Modifier": char_setup_modifier,
    }


def fetch_characters_info():
    soup = gimmie_soup()

    char_info = {}

    character_links = soup.select("div.mw-category-generated ul li a[href]")

    # TODO
    # Temporary limit the number of requests to the server!
    cutoff = 10

    for link in character_links:
        # TODO
        # Temporary limit the number of requests to the server!
        if cutoff == 0:
            break
        cutoff -= 1

        character_name = link.text
        character_url = "https://wiki.bloodontheclocktower.com" + link["href"]
        char_info[character_name] = fetch_character_info(character_url)

    return char_info


def print_characters_info(char_info):
    for char_name, data in char_info.items():
        print(f"\nName: {char_name}")
        print(f"Version: {data['Version']}")
        print(f"Type: {data['Type']}")
        print(f"Ability: {data['Ability']}")
        if data["Setup Modifier"] is not None:
            print(f"Setup Modifier: [{data['Setup Modifier']}]\n")


def store_data_to_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    except IOError as e:
        print(f"Error writing to file {filename}: {e}")


characters_info = fetch_characters_info()
print_characters_info(characters_info)
store_data_to_file(characters_info, ".\\character_data\\character_data.json")
