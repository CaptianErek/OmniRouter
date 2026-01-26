import requests
from openrouter import OpenRouter
from pathlib import Path
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv
from utils.providers.database import Session,Model
from sqlalchemy import inspect
import polars as pl

basepath = Path(__file__).resolve().parent.parent.parent
load_dotenv(basepath / ".env")

class Cloud_Providers():
    def __init__(self) -> None:
        pass

    def groq_models(self):
        api_key = os.getenv("GROQ-API-KEY")
        url = "https://api.groq.com/openai/v1/models"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching Groq models: {response.text}")
            return []

        all_models = response.json()["data"]
        avaliable_model_ids = {"llama-3.1-8b-instant" : None,"llama-3.3-70b-versatile" : None,"meta-llama/llama-guard-4-12b" : "meta-llama/Llama-Guard-4-12B","openai/gpt-oss-120b" : "openai/gpt-oss-120b","openai/gpt-oss-20b" : "openai/gpt-oss-20b"}

        avaliable_model = []
        for info in all_models:
            if info["id"] in list(avaliable_model_ids.keys()):
                index = list(avaliable_model_ids.keys()).index(info["id"])
                avaliable_model.append({"id" : info["id"], 
                                        "publisher" : info["owned_by"],
                                        "max_tokens" : info["max_completion_tokens"],
                                        "provider" : "groq",
                                        "type" : "cloud",
                                        "hugging_face_model_id" : list(avaliable_model_ids.values())[index]})
        
        return avaliable_model

    def openroute_models(self):
        api_key = os.getenv("OPENROUTER-API-KEY")
        with OpenRouter(api_key=api_key) as client:
            all_models = client.models.list()
        models = all_models.data
        text_to_text_models = [
            m for m in models
            if getattr(m.architecture, "modality", None) == "text->text"
        ]

        avaliable_models = []

        for model in text_to_text_models:
            avaliable_models.append({
                "id" : model.id,
                "publisher" : model.name.split(" " and ":")[0].split(" ")[0],
                "max_tokens" : model.top_provider.max_completion_tokens,
                "provider" : "openroute",
                "type" : "cloud",
                "hugging_face_model_id" : None if model.hugging_face_id == "" or None else model.hugging_face_id
            })

        return avaliable_models
    
    def load_data(self):
        session = Session()
        models = self.groq_models()
        models.extend(self.openroute_models())

        df = pl.DataFrame(models)
        df = df.unique(subset=["id"])
        models = df.to_dicts()

        existing_model_ids = [m.model_id for m in session.query(Model).all()]

        for model in models:
            if model["id"] not in existing_model_ids:
                model1 = Model(
                    id = uuid.uuid4().hex,
                    model_id = model["id"],
                    publisher = model["publisher"],
                    max_tokens = model["max_tokens"],
                    provider = model["provider"],
                    type = model["type"],
                    hugging_face_model_id = model["hugging_face_model_id"]
                )
                session.add(model1)
        session.commit()
        return

if __name__ == "__main__":
    Cloud_Providers().load_data()