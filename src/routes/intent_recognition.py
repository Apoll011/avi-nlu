from typing_extensions import Annotated
from fastapi import APIRouter, Depends, Query
from src.utils import get_kit
from src.config import engine_base_path
from snips_nlu.dataset import Dataset, Intent
from snips_nlu.dataset.entity import Entity
from src.models import Data, IntentRecongnitionEngineTrainType
import os
import json

intent_router = APIRouter()


@intent_router.get("/installed", name="Returns the instaled engines")
async def intent_installed():
    try:
        return {
            "response": {
                "instaled": list(
                    filter(
                        lambda e: os.path.isdir(f"{engine_base_path}/{e}"),
                        os.listdir(engine_base_path),
                    )
                ),
                "data": {
                    lang: json.load(
                        open(f"{engine_base_path}/{lang}/nlu_engine.json", "r")
                    )["dataset_metadata"]
                    for lang in os.listdir(engine_base_path)
                    if os.path.isdir(f"{engine_base_path}/{lang}")
                },
            }
        }
    except Exception as e:
        return {"response": False, "error": str(e)}


@intent_router.get("/engine", name="Train or Reuse the Intent Recognition Engine")
async def intent_train(
    type: IntentRecongnitionEngineTrainType = IntentRecongnitionEngineTrainType.REUSE,
    intentKit=Depends(get_kit),
):
    try:
        if type == IntentRecongnitionEngineTrainType.REUSE:
            intentKit.reuse()
        else:
            intentKit.train()
        return {
            "response": {"result": True, "action": type.value, "lang": intentKit.lang}
        }
    except Exception as e:
        return {"response": False, "error": str(e)}


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
)
async def intent_populate(dataset: Data, intentKit=Depends(get_kit)):
    try:
        if dataset.language != intentKit.lang:
            return {
                "error": f"Wrong Language Dataset expected, {intentKit.lang}",
                "lang": intentKit.lang,
            }
        intentKit.populate(convert(dataset))
        return {"response": True}
    except AttributeError:
        return {"error": "Engine not trained"}
    except Exception as e:
        return {"response": False, "error": str(e)}


@intent_router.get(
    "/",
    name="Recognize intent from sentence",
    description="This will recognize the intent from a givin sentence and return the result parsed",
)
async def intent_reconize(
    text: Annotated[str, Query(max_length=250, min_length=2)],
    intentKit=Depends(get_kit),
):
    try:
        return {"response": intentKit.parse(text)}
    except AttributeError:
        return {"error": "Engine not trained", "response": None}
    except Exception as e:
        return {"response": None, "error": str(e)}
