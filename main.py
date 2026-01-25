from datetime import datetime, timedelta
import re

from snips_nlu.dataset import Dataset, Intent
from snips_nlu.dataset.entity import Entity
import typer
import os
import lingua_franca
import lingua_franca.parse
import lingua_franca.format
from src.models import Data, IntentRecongnitionEngineTrainType, Lang
from src.kit import IntentKit
from fastapi import Depends, FastAPI, Query, Request
from src.config import __version__, engine_base_path
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn

lingua_franca.load_languages(["en", "pt"])

if not os.path.exists(engine_base_path):
    os.makedirs(engine_base_path)

app = FastAPI(
    title="Avi Server",
    version=__version__,
    description="Avi api server that handles complex and heavy tasks such as nlp etc.",
    summary="Avi base server used for handling heavy functions",
    contact={"name": "Tiago Bernardo", "email": "tiagorobotik@gmail.com"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

cli = typer.Typer()


def get_kit(request: Request) -> IntentKit:
    return request.app.state.intentKit


@app.get("/", name="Route")
async def route():
    return {"response": {"name": "Avi"}}


@app.get(
    "/avi/alive",
    name="Check If Alive",
    description="This checks if Avi is running and send the basic values",
)
async def alive(intentKit=Depends(get_kit)):
    response = {
        "on": True,
        "kit": {
            "all_on": True and intentKit.loaded,
            "intent": intentKit.loaded,
        },
        "version": __version__,
    }
    return {"response": response}


@app.get(
    "/intent_recognition/engine", name="Train or Reuse the Intent Recognition Engine"
)
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


@app.post(
    "/intent_recognition/populate",
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


@app.get(
    "/intent_recognition/",
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
        return {"error": "Engine not trained"}


@app.get("/close")
async def close():
    return {"response": True}


@app.get("/lang")
async def lang_base():
    return {"response": lingua_franca.get_supported_langs()}


@app.get("/lang/parse/extract_numbers")
def extract_numbers(
    text: str, short_scale: bool = True, ordinals: bool = False, lang: str = ""
):
    """
        Takes in a string and extracts a list of numbers.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        list: list of extracted numbers as floats, or empty list if none found
    """
    return {
        "response": lingua_franca.parse.extract_numbers(
            text, short_scale, ordinals, lang
        )
    }


@app.get("/lang/parse/extract_number")
def extract_number(text, short_scale=True, ordinals=False, lang=""):
    """Takes in a string and extracts a number.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        (int, float or False): The number extracted or False if the input
                               text contains no numbers
    """
    return {
        "response": lingua_franca.parse.extract_number(
            text, short_scale, ordinals, lang
        )
    }


@app.get("/lang/parse/extract_duration")
def extract_duration(text, lang=""):
    """Convert an english phrase into a number of seconds

    Convert things like:

    * "10 minute"
    * "2 and a half hours"
    * "3 days 8 hours 10 minutes and 49 seconds"

    into an int, representing the total number of seconds.

    The words used in the duration will be consumed, and
    the remainder returned.

    As an example, "set a timer for 5 minutes" would return
    ``(300, "set a timer for")``.

    Args:
        text (str): string containing a duration
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.

    Returns:
        (timedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.
    """
    return {"response": lingua_franca.parse.extract_duration(text, lang)}


@app.get("/lang/parse/extract_datetime")
def extract_datetime(text, lang=""):
    """
    Extracts date and time information from a sentence.  Parses many of the
    common ways that humans express dates and times, including relative dates
    like "5 days from today", "tomorrow', and "Tuesday".

    Vague terminology are given arbitrary values, like:
        - morning = 8 AM
        - afternoon = 3 PM
        - evening = 7 PM

    If a time isn't supplied or implied, the function defaults to 12 AM

    Args:
        text (str): the text to be interpreted
        lang (str): the BCP-47 code for the language to use, None uses default

    Returns:
        [:obj:`datetime`, :obj:`str`]: 'datetime' is the extracted date
            as a datetime object in the local timezone.
            'leftover_string' is the original phrase with all date and time
            related keywords stripped out. See examples for further
            clarification

            Returns 'None' if no date or time related text is found.

    Examples:

        >>> extract_datetime(
        ... "What is the weather like the day after tomorrow?",
        ... datetime(2017, 6, 30, 00, 00)
        ... )
        [datetime.datetime(2017, 7, 2, 0, 0), 'what is weather like']

        >>> extract_datetime(
        ... "Set up an appointment 2 weeks from Sunday at 5 pm",
        ... datetime(2016, 2, 19, 00, 00)
        ... )
        [datetime.datetime(2016, 3, 6, 17, 0), 'set up appointment']

        >>> extract_datetime(
        ... "Set up an appointment",
        ... datetime(2016, 2, 19, 00, 00)
        ... )
        None
    """
    return {
        "response": lingua_franca.parse.extract_datetime(
            text, lang=lang, anchorDate=None, default_time=None
        )
    }


@app.get("/lang/parse/normalize")
def normalize(text, lang="", remove_articles=True):
    """Prepare a string for parsing

    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.

    Args:
        text (str): the string to normalize
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        remove_articles (bool): whether to remove articles (like 'a', or
                                'the'). True by default.

    Returns:
        (str): The normalized string.
    """
    return {"response": lingua_franca.parse.normalize(text, lang, remove_articles)}


@app.get("/lang/parse/is_fractional")
def is_fractional(input_str, short_scale=True, lang=""):
    """
    This function takes the given text and checks if it is a fraction.
    Used by most of the number exractors.

    Will return False on phrases that *contain* a fraction. Only detects
    exact matches. To pull a fraction from a string, see extract_number()

    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction
    """
    return {"response": lingua_franca.parse.is_fractional(input_str, short_scale, lang)}


@app.get("/lang/format/nice_number")
def nice_number(number, lang="", speech=True, denominators=[]):
    """Format a float to human readable functions

    This function formats a float to human understandable functions. Like
    4.5 becomes 4 and a half for speech and 4 1/2 for text
    Args:
        number (int or float): the float to format
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """
    return {
        "response": lingua_franca.format.nice_number(
            float(number), lang, speech, list(map(lambda x: int(x), denominators))
        )
    }


@app.get("/lang/format/nice_time")
def nice_time(dt=None, lang="", speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'five thirty' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
        variant (string): alternative time system to be used, string must
                          match language specific mappings
    Returns:
        (str): The formatted time string
    """
    n = datetime.now() + timedelta(hours=1)
    return {
        "response": lingua_franca.format.nice_time(
            dt if dt is not None else n, lang, speech, use_24hour, use_ampm
        )
    }


@app.get("/lang/format/pronounce_number")
def pronounce_number(number: int, lang="", places=2):
    """
    Convert a number to it's spoken equivalent

    For example, '5' would be 'five'

    Args:
        number: the number to pronounce
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        places (int): number of decimal places to express, default 2
    Returns:
        (str): The pronounced number
    """
    return {"response": lingua_franca.format.pronounce_number(number, lang, places)}


@app.get("/lang/format/nice_duration")
def nice_duration(duration: int, lang="", speech=True):
    """Convert duration in seconds to a nice spoken timespan

    Examples:
       duration = 60  ->  "1:00" or "one minute"
       duration = 163  ->  "2:43" or "two minutes forty three seconds"

    Args:
        duration: time, in seconds
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
        speech (bool): format for speech (True) or display (False)

    Returns:
        str: timespan as a string
    """
    return {"response": lingua_franca.format.nice_duration(duration, lang, speech)}


@app.get("/lang/format/nice_relative_time")
def nice_relative_time(when, relative_to=None, lang=None):
    """Create a relative phrase to roughly describe the period between two
    datetimes.

    Examples are "25 seconds", "tomorrow", "7 days".

    Note: The reported period is currently limited to a number of days. Longer
          periods such as multiple weeks or months will be reported in days.

    Args:
        when (datetime): Local timezone
        relative_to (datetime): Baseline for relative time, default is now()
        lang (str, optional): Defaults to "en-us".
    Returns:
        str: Relative description of the given time
    """
    return {
        "response": lingua_franca.format.nice_relative_time(when, relative_to, lang)
    }


@cli.command()
def train(
    lang: Annotated[
        Lang, typer.Argument(help="The language to train the engine with")
    ] = Lang.EN,
):
    """
    Trains the engine on a specified language and saves the engine on the engine data folder
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Training...", total=None)
        intentKit.train(lang)


@cli.command()
def serve(
    lang: Lang = Lang.EN,
    host: Annotated[str, typer.Argument(help="THe host IP.")] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Argument(
            help="The server port. Unless that you edit the port on Avi too, dont change this."
        ),
    ] = 1178,
):
    """
    Starts a web api for AVI NLU
    """
    import uvicorn

    try:
        print("=" * 50)
        print("Press Ctrl+C to stop")
        print("Waiting for application startup.")
        print(f"App started on http://{host}:{port}")
        print("=" * 50)
        app.state.intentKit = IntentKit(lang)
        uvicorn.run(app, host=host, port=port, log_level="warning")

    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        import traceback

        traceback.print_exc()
        input("Press Enter to exit...")


@cli.command()
def version():
    """
    The current Avi Version
    """
    print("AVI NLU v" + __version__)
    print("Made by Tiago Inês, at Embrasse Studio.")


if __name__ == "__main__":
    cli()
