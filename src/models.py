from enum import Enum


class Lang(str, Enum):
    EN = "en"
    PT = "pt"


class IntentRecongnitionEngineTrainType(str, Enum):
    TRAIN = "train"
    REUSE = "reuse"
