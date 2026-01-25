from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from pydantic import BaseModel


class Lang(str, Enum):
    EN = "en"
    PT = "pt"


class Slot(BaseModel):
    name: str
    entity: str

    def as_dict(self) -> dict:
        return {"name": self.name, "entity": self.entity}


class Intent(BaseModel):
    type: str = "intent"
    name: str
    utterances: List[str]
    slots: List[Slot]

    def as_dict(self) -> dict:
        return {
            "type": "intent",
            "name": self.name,
            "utterances": self.utterances,
            "slots": map(lambda s: s.as_dict(), self.slots),
        }


class Entity(BaseModel):
    type: str = "entity"
    name: str
    values: List[Union[str, List[str]]]
    automatically_extensible: bool = True
    use_synonyms: bool = True
    matching_strictness: float = 1.0

    def as_dict(self) -> dict:
        return {
            "type": "entity",
            "values": self.values,
            "name": self.name,
            "automatically_extensible": self.automatically_extensible,
            "use_synonyms": self.use_synonyms,
            "matching_stricness": self.matching_strictness,
        }


class Data(BaseModel):
    language: Lang
    data: List[Union[Entity, Intent]]


class IntentRecongnitionEngineTrainType(str, Enum):
    TRAIN = "train"
    REUSE = "reuse"
