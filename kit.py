import io
import os
import json
import uuid
from math import exp
from difflib import get_close_matches
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_EN, CONFIG_PT_PT

class IntentKit:
    
    engine = None
    loaded = False
    def __init__(self):
        self.lang = None
    
    def reuse(self, lang = "en"):
        if self.lang != lang:
            self.lang = lang
            self.engine = SnipsNLUEngine.from_path(f"./features/intent_recognition/snips/engine/{lang}")
            self.loaded = True

    def train(self, lang = "en"):
        test = "en" if lang=="en" else "pt_pt"
        os.system(f"snips-nlu generate-dataset {test} ./features/intent_recognition/snips/data/{lang}.yaml > ./features/intent_recognition/snips/dataset/dataset_{lang}.json")
        with io.open(f"./features/intent_recognition/snips/dataset/dataset_{lang}.json") as f:
            dataset = json.load(f)
        
        if self.engine is not None:
            del self.engine
        self.engine = SnipsNLUEngine(config=CONFIG_EN if lang == "en" else CONFIG_PT_PT)
        self.engine.fit(dataset)
        os.system(f"rm -rf ./features/intent_recognition/snips/engine/{lang}/")
        self.engine.persist(f"./features/intent_recognition/snips/engine/{lang}")
        self.loaded = True
        self.lang = lang

    def parse(self, text):
        if isinstance(self.engine, SnipsNLUEngine):
            return self.engine.parse(text)
        else:
            raise Exception("Intent recognition Engine not loaded")