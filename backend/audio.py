"""
This module contains the logic for audio file management, including the creation and allocation of 
them.
"""

from pathlib import Path
from server import Listener, ProficiencyLevel

class AudioFile:
    def __init__(self, path: Path, requirements: dict[str, ProficiencyLevel]) -> None:
        self.path = path
        self.requirements = requirements
    def is_eligible(self, listener: Listener) -> bool:
        is_eligible = True
        for lang, proficiency in self.requirements:
            # TODO: check if it works like this
            if listener.languages[lang] < proficiency:
                is_eligible = False
        return is_eligible

