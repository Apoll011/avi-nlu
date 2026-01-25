import os
from typing_extensions import Optional

from snips_nlu import SnipsNLUEngine
from snips_nlu.dataset import Dataset
from snips_nlu.default_configs import CONFIG_EN, CONFIG_PT_PT
from src.models import Lang
from src.config import intents_data_folder


class IntentKit:
    engine = None
    loaded = False
    data: Optional[Dataset] = None
    lang: Lang = Lang.EN
    engine_path: str

    def __init__(self, lang: Lang = Lang.EN) -> None:
        self.lang = lang
        self.engine_path = f"{intents_data_folder}/engine/{lang}"

    def populate(self, data: Dataset):
        self.data = data

    def reuse(self):
        if os.path.exists(self.engine_path):
            self.engine = SnipsNLUEngine.from_path(self.engine_path)
            self.loaded = True
        elif not os.path.exists(self.engine_path):
            self.train()

    def train(self):
        if self.engine is not None:
            del self.engine

        if self.data is None:
            raise Exception("Please populate the data first")

        self.engine = SnipsNLUEngine(
            config=CONFIG_EN if self.lang == "en" else CONFIG_PT_PT
        )
        self.engine.fit(self.data)

        if not os.path.exists(self.engine_path):
            os.makedirs(self.engine_path)
        else:
            os.system(f"rm -rf {self.engine_path}/")

        self.engine.persist(self.engine_path)
        self.loaded = True

    def parse(self, text):
        if not self.loaded or not isinstance(self.engine, SnipsNLUEngine):
            raise Exception("Intent recognition Engine not loaded")
        return self.engine.parse(text)
