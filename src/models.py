from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Union

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


class EngineTrainType(str, Enum):
    TRAIN = "train"
    REUSE = "reuse"


class Processor(str, Enum):
    AI = "ai"
    ENGINE = "engine"


class Route(BaseModel):
    name: str


class Alive(BaseModel):
    on: bool
    intent_kit: bool
    version: str


class Installed(BaseModel):
    installed: List[str]
    data: Dict[str, Dict]


class EngineTrain(BaseModel):
    result: bool
    action: EngineTrainType
    lang: Lang


class Created(BaseModel):
    created: bool = True


class Recognized(BaseModel):
    result: Dict
    processor: Processor


class AppError(Exception):
    status_code: int
    code: str
    message: str

    def __init__(self, message: str):
        self.message = message


class EngineTrainError(AppError):
    status_code = 500
    code = "ENGINE_TRAIN_ERROR"

    def __init__(self, type: EngineTrainType, error: str):
        super().__init__(f"Error {type.value} the engine: {error}")


class EngineNotTrained(AppError):
    status_code = 500
    code = "ENGINE_NOT_TRAINED"

    def __init__(self):
        super().__init__("Engine not trained, Please train or re-use it.")


class IntentError(AppError):
    status_code = 500
    code = "INTENT_ERROR"


class WrongDataset(AppError):
    status_code = 422
    code = "DATASET_ERROR"


class WrongLanguage(AppError):
    status_code = 400
    code = "NOT_THE_CURRENT_LANGUAGE"

    def __init__(self, lang: Lang):
        super().__init__(f"Wrong Language Dataset expected, {lang}")
