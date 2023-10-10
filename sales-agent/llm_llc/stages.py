from typing import Dict
import json

import sys


def load_stages(cls, stages_file):
    with open(stages_file, "r") as json_file:
        cls.stages = json.load(json_file)


class ConversationStages:
    stages: Dict = []

    @classmethod
    def load_stages(cls, stages_file):
        with open(stages_file, "r") as json_file:
            cls.stages = json.load(json_file)

    @classmethod
    def to_str(cls) -> str:
        if not cls.stages:
            cls.load_stages("kb/stages.json")

        return "\n".join(
            [str(key) + ": " + str(value) for key, value in cls.stages.items()]
        )

    @classmethod
    def get_init(cls) -> str:
        if not cls.stages:
            cls.load_stages("kb/stages.json")
        return cls.stages.get("1")

    @classmethod
    def get_dict(cls) -> str:
        if not cls.stages:
            cls.load_stages("kb/stages.json")
        return cls.stages
