from Errors import *

class TownSquare():
    def __init__(self, not_in_play_characters):
        self.not_in_play_characters = not_in_play_characters

        self.in_play_characters = []

    def assign(self, character):
        # Verify the character is currently not in play
        if not any(not_in_play_character.name == character.name for not_in_play_character in self.not_in_play_characters):
            return False, WarningAddCharacterNotNotInPlay.format(character.name)

        # Verify the character isn't somehow already in play
        if any(in_play_character.name == character.name for in_play_character in self.in_play_characters):
            return False, WarningAddCharacterAlreadyInPlay.format(character.name)

        # Add the new character to the Town Square
        self.in_play_characters.append(character)

        # Remove the character from the list of not-in-play characters
        self.not_in_play_characters = list( filter(lambda x: x.name == character.name, self.not_in_play_characters) )