from enum import Enum


class BrewMethod(str, Enum):
    AEROPRESS = "aeropress"
    POUROVER = "pourover"
    ESPRESSO = "espresso"
    FRENCH_PRESS = "french_press"
