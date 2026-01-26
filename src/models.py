from enum import Enum
from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel, Field


class Lang(str, Enum):
    """Supported languages for the NLU engine."""

    EN = "en"
    PT = "pt"


class InputSlot(BaseModel):
    """Represents a slot definition for an intent."""

    name: str = Field(
        ...,
        description="Name of the slot (e.g., 'city', 'date', 'product_name')",
        examples=["location", "time", "person_name"],
    )
    entity: str = Field(
        ...,
        description="Entity type this slot should extract (must match an existing entity name)",
        examples=["city", "datetime", "person"],
    )

    def as_dict(self) -> dict:
        return {"name": self.name, "entity": self.entity}


class InputIntent(BaseModel):
    """Defines an intent with training utterances and slot mappings."""

    type: str = Field(
        default="intent",
        description="Type identifier for intent objects",
    )
    name: str = Field(
        ...,
        description="Unique name for the intent",
        examples=["book_flight", "check_weather", "order_product"],
        min_length=1,
    )
    utterances: List[str] = Field(
        ...,
        description="Training examples showing different ways users might express this intent",
        examples=[["book a flight to Paris", "I want to fly to London"]],
        min_length=1,
    )
    slots: List[InputSlot] = Field(
        default_factory=list,
        description="Slots to extract from utterances matching this intent",
    )

    def as_dict(self) -> dict:
        return {
            "type": "intent",
            "name": self.name,
            "utterances": self.utterances,
            "slots": list(map(lambda s: s.as_dict(), self.slots)),
        }


class Entity(BaseModel):
    """Defines a custom entity type for slot extraction."""

    type: str = Field(
        default="entity",
        description="Type identifier for entity objects",
    )
    name: str = Field(
        ...,
        description="Unique name for the entity",
        examples=["product_category", "city_name", "color"],
        min_length=1,
    )
    values: List[Union[str, List[str]]] = Field(
        ...,
        description="List of entity values. Can be strings or lists of synonyms (first item is canonical value)",
        examples=[
            ["red", "crimson", "scarlet"],
            "blue",
            ["NYC", "New York", "New York City"],
        ],
        min_length=1,
    )
    automatically_extensible: bool = Field(
        default=True,
        description="Whether the engine can recognize values similar to but not exactly matching the provided values",
    )
    use_synonyms: bool = Field(
        default=True,
        description="Whether to use synonym matching for entity resolution",
    )
    matching_strictness: float = Field(
        default=1.0,
        description="Strictness of entity matching (0.0 to 1.0). Higher values require closer matches",
        ge=0.0,
        le=1.0,
    )

    def as_dict(self) -> dict:
        return {
            "type": "entity",
            "values": self.values,
            "name": self.name,
            "automatically_extensible": self.automatically_extensible,
            "use_synonyms": self.use_synonyms,
            "matching_strictness": self.matching_strictness,
        }


class Data(BaseModel):
    """Training dataset containing entities and intents for a specific language."""

    language: Lang = Field(..., description="Target language for this dataset")
    data: List[Union[Entity, InputIntent]] = Field(
        ...,
        description="Collection of entities and intents to train the NLU engine",
        min_length=1,
    )


class Range(BaseModel):
    """Character position range in the input text."""

    start: int = Field(..., description="Starting character index (inclusive)", ge=0)
    end: int = Field(..., description="Ending character index (exclusive)", ge=0)


class SlotValue(BaseModel):
    """Resolved value of an extracted slot."""

    kind: Literal["Custom"] = Field(..., description="Type of slot value resolution")
    value: str = Field(..., description="Canonical/resolved value of the slot")


class Slot(BaseModel):
    """Extracted slot from user input."""

    range: Range = Field(
        ..., description="Character range where this slot was found in the input"
    )
    rawValue: str = Field(..., description="Exact text extracted from the user input")
    value: SlotValue = Field(
        ..., description="Resolved slot value after entity matching"
    )
    entity: str = Field(..., description="Entity type of this slot")
    slotName: str = Field(..., description="Name of the slot as defined in the intent")


class Intent(BaseModel):
    """Recognized intent from user input."""

    intentName: str = Field(
        ...,
        description="Name of the matched intent",
        examples=["book_flight", "check_weather"],
    )
    probability: float = Field(
        ...,
        description="Confidence score for this intent classification (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )


class NLUResult(BaseModel):
    """Complete NLU parsing result including intent and extracted slots."""

    input: str = Field(..., description="Original user input text that was parsed")
    intent: Intent = Field(..., description="Recognized intent with confidence score")
    slots: List[Slot] = Field(
        default_factory=list, description="List of extracted slots from the input"
    )


class Action(BaseModel):
    """Represents a single action in an execution plan."""

    id: str = Field(
        ...,
        description="Unique action identifier used for referencing in conditions",
        examples=["action_1", "fetch_weather", "send_email"],
    )
    function: str = Field(
        ...,
        description="Function name to execute (can be core function or skill-specific)",
        examples=["get_weather", "book_flight", "send_notification"],
    )
    args: Dict[str, Any] = Field(
        default_factory=dict, description="Arguments to pass to the function"
    )
    condition: Optional[str] = Field(
        None,
        description="Optional condition expression referencing previous action results (e.g., 'action_1.success')",
    )


class ActionPlan(BaseModel):
    """Sequence of actions to be executed."""

    actions: List[Action] = Field(
        ..., description="Ordered list of actions to execute", min_length=1
    )


class EngineTrainType(str, Enum):
    """Training operation type."""

    TRAIN = "train"  # Train a new model
    REUSE = "reuse"  # Reuse existing trained model


class Processor(str, Enum):
    """Type of processor that handled the request."""

    AI = "ai"  # Processed by AI/LLM
    ENGINE = "engine"  # Processed by NLU engine


class Route(BaseModel):
    """API route information."""

    name: str = Field(..., description="Voice Assisntant Name")


class Alive(BaseModel):
    """Health check response indicating service status."""

    on: bool = Field(..., description="Whether the main service is operational")
    intent_kit: bool = Field(
        ..., description="Whether the intent kit/NLU engine is available"
    )
    version: str = Field(
        ..., description="Current service version", examples=["v1.0.0", "v2.1.3"]
    )


class Installed(BaseModel):
    """Information about installed skills/modules."""

    installed: List[str] = Field(..., description="List of avaliable engines")
    data: Dict[str, Dict] = Field(
        ..., description="Detailed information about each engine"
    )


class EngineTrain(BaseModel):
    """Training operation result."""

    result: bool = Field(..., description="Whether the training operation succeeded")
    action: EngineTrainType = Field(
        ..., description="Type of training operation that was performed"
    )
    lang: Lang = Field(..., description="Language for which the engine was trained")


class Created(BaseModel):
    """Indicates that the Engines was correctly populated"""

    created: bool = Field(
        default=True, description="Indicates successful engine populate"
    )


class Recognized(BaseModel):
    """Recognition result from either AI or NLU engine."""

    result: Union[ActionPlan, NLUResult] = Field(
        ...,
        description="Recognition result: ActionPlan if processed by AI, NLUResult if processed by engine",
    )
    processor: Processor = Field(
        ..., description="Which processor handled this request"
    )


# Exception classes
class AppError(Exception):
    """Base application error."""

    status_code: int
    code: str
    message: str

    def __init__(self, message: str):
        self.message = message


class EngineTrainError(AppError):
    """Error during engine training process."""

    status_code = 500
    code = "ENGINE_TRAIN_ERROR"

    def __init__(self, type: EngineTrainType, error: str):
        super().__init__(f"Error {type.value} the engine: {error}")


class EngineNotTrained(AppError):
    """Error when attempting to use an untrained engine."""

    status_code = 500
    code = "ENGINE_NOT_TRAINED"

    def __init__(self):
        super().__init__("Engine not trained, Please train or re-use it.")


class IntentError(AppError):
    """Generic intent processing error."""

    status_code = 500
    code = "INTENT_ERROR"


class WrongDataset(AppError):
    """Error for malformed or invalid dataset."""

    status_code = 422
    code = "DATASET_ERROR"


class WrongLanguage(AppError):
    """Error when dataset language doesn't match expected language."""

    status_code = 400
    code = "NOT_THE_CURRENT_LANGUAGE"

    def __init__(self, lang: Lang):
        super().__init__(f"Wrong Language Dataset expected, {lang}")
