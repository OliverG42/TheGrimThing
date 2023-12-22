from Scripts import TestingBrewing
from TownSquare import TownSquare


def test_basic_adding_characters():
    town_square = TownSquare(TestingBrewing)

    assert(town_square.not_in_play_characters == TestingBrewing)
    assert(town_square.in_play_characters == [])

    # town_square.assign()