from snips_nlu.exceptions import (
    DatasetFormatError,
    SnipsNLUError,
)
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from src.utils import get_kit
from src.config import engine_base_path
from snips_nlu.dataset import Dataset, Intent
from snips_nlu.dataset.entity import Entity
from src.models import (
    Created,
    Data,
    EngineNotTrained,
    EngineTrain,
    EngineTrainError,
    ErrorResponse,
    Installed,
    EngineTrainType,
    IntentError,
    Recognized,
    WrongDataset,
    WrongLanguage,
)
import os
import json

intent_router = APIRouter()


@intent_router.get("/installed", name="Returns the instaled engines")
async def intent_installed() -> Installed:
    return Installed(
        installed=list(
            filter(
                lambda e: os.path.isdir(f"{engine_base_path}/{e}"),
                os.listdir(engine_base_path),
            )
        ),
        data={
            lang: json.load(open(f"{engine_base_path}/{lang}/nlu_engine.json", "r"))[
                "dataset_metadata"
            ]
            for lang in os.listdir(engine_base_path)
            if os.path.isdir(f"{engine_base_path}/{lang}")
        },
    )


@intent_router.post(
    "/engine",
    name="Train or Reuse the Intent Recognition Engine",
    responses={
        500: {
            "description": "Error Training or reusing the model",
            "model": ErrorResponse,
        }
    },
)
async def intent_train(
    type: EngineTrainType = EngineTrainType.REUSE,
    intentKit=Depends(get_kit),
) -> EngineTrain:
    try:
        if type == EngineTrainType.REUSE:
            intentKit.reuse()
        else:
            intentKit.train()
        return EngineTrain(result=True, action=type, lang=intentKit.lang)
    except Exception as e:
        raise EngineTrainError(type, str(e))


def load(data: Data):
    intents = []
    entities = []
    for doc in data.data:
        doc_type = doc.type
        if doc_type == "entity":
            entities.append(Entity.from_yaml(doc.as_dict()))
        elif doc_type == "intent":
            intents.append(Intent.from_yaml(doc.as_dict()))
    return intents, entities


def convert(d: Data) -> Dataset:
    intents, entities = load(d)
    return Dataset(d.language, intents, entities)


@intent_router.post(
    "/populate",
    name="Define the intent and entities",
    description="Set the current lang dataset",
    status_code=202,
    responses={
        500: {
            "description": "Engine not trained",
            "model": ErrorResponse,
        },
        409: {
            "description": "Worng language on the dataset",
            "model": ErrorResponse,
        },
        400: {
            "description": "Dataset has invalid data",
            "model": ErrorResponse,
        },
    },
)
async def intent_populate(dataset: Data, intentKit=Depends(get_kit)) -> Created:
    try:
        if dataset.language != intentKit.lang:
            raise WrongLanguage(intentKit.lang)
        intentKit.populate(convert(dataset))
        return Created()

    except DatasetFormatError as e:
        raise WrongDataset(str(e))
    except AttributeError:
        raise EngineNotTrained()


@intent_router.get(
    "/",
    name="Recognize intent from sentence",
    description="This will recognize the intent from a givin sentence and return the result parsed",
    responses={
        500: {
            "description": "Engine not trained",
            "model": ErrorResponse,
        },
        502: {
            "description": "Error getting the intent",
            "model": ErrorResponse,
        },
    },
)
async def intent_reconize(
    text: Annotated[str, Query(max_length=250, min_length=2)],
    intentKit=Depends(get_kit),
) -> Recognized:
    try:
        data, processor = intentKit.parse(text)
        return Recognized(result=data, processor=processor)
    except AttributeError:
        raise EngineNotTrained()
    except SnipsNLUError as e:
        raise IntentError(str(e))
