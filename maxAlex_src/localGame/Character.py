from typing import Dict, Union

class Character:
    """
        Class representing the eight possible characters of the game.
    """
    color: str
    suspect: bool
    position: int
    power_activated: bool

    def __init__(self, color: str, sus: bool = False, pos: int = 0, pow: bool = False):
        self.color = color
        self.suspect = sus
        self.position = pos
        self.power_activated = pow

    def __repr__(self):
        if self.suspect:
            susp = "-suspect"
        else:
            susp = "-clean"
        return self.color + "-" + str(self.position) + susp

    def update(self, new_dict):
        if (type(new_dict) == dict):
            self.color = new_dict["color"]
            self.suspect = new_dict["suspect"]
            self.position = new_dict["position"]
            self.power_activated = new_dict["power"]
        else:
            self.color = new_dict.color
            self.suspect = new_dict.suspect
            self.position = new_dict.position
            self.power_activated = new_dict.power_activated

    def display(self)-> Dict[str, Union[bool, int, str]]:
        return {
            "color": self.color,
            "suspect": self.suspect,
            "position": self.position,
            "power": self.power_activated
        }
