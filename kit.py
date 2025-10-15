import io
import os
import json

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
        print(f"[IntentKit] Starting training for language: {lang}")
        test = "en" if lang=="en" else "pt_pt"
        print(f"[IntentKit] Generating dataset with snips-nlu for locale '{test}' from YAML: ./features/intent_recognition/snips/data/{lang}.yaml")
        os.system(f"snips-nlu generate-dataset {test} ./features/intent_recognition/snips/data/{lang}.yaml > ./features/intent_recognition/snips/dataset/dataset_{lang}.json")
        dataset_path = f"./features/intent_recognition/snips/dataset/dataset_{lang}.json"
        print(f"[IntentKit] Loading generated dataset: {dataset_path}")
        with io.open(dataset_path) as f:
            dataset = json.load(f)
        print(f"[IntentKit] Dataset loaded. Intents: {len(dataset.get('intents', {}))}, Entities: {len(dataset.get('entities', {}))}")
        
        if self.engine is not None:
            print("[IntentKit] Releasing previous engine instance")
            del self.engine
        print("[IntentKit] Initializing SnipsNLUEngine with appropriate config")
        self.engine = SnipsNLUEngine(config=CONFIG_EN if lang == "en" else CONFIG_PT_PT)
        print("[IntentKit] Fitting engine with dataset...")
        self.engine.fit(dataset)
        print("[IntentKit] Fit complete")
        engine_dir = f"./features/intent_recognition/snips/engine/{lang}"
        print(f"[IntentKit] Removing existing engine directory (if any): {engine_dir}")
        os.system(f"rm -rf {engine_dir}/")
        print(f"[IntentKit] Persisting engine to: {engine_dir}")
        self.engine.persist(engine_dir)
        self.loaded = True
        self.lang = lang
        print(f"[IntentKit] Training finished for '{lang}'. Engine ready.")

    def parse(self, text):
        if isinstance(self.engine, SnipsNLUEngine):
            return self.engine.parse(text)
        else:
            raise Exception("Intent recognition Engine not loaded")