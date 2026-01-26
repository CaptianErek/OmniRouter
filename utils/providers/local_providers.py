import psutil
import torch
from fastapi import HTTPException
import polars as pl
import uuid
from utils.providers.database import Session,Model

class ConfigError(Exception):
    pass

class Local_Provider():
    def __init__(self) -> None:
        pass

    def hardware(self):
        try:
            cpu_cores = psutil.cpu_count(logical=True)
            ram_avaliable = round(psutil.virtual_memory().total/(1024 ** 3),2)

            gpu_avaliable = None
            vram_avaliable = None

            if torch.cuda.is_available():
                gpu_avaliable = torch.cuda.get_device_name(0)
                vram_avaliable = round(torch.cuda.get_device_properties(0).total_memory/(1024 ** 3),2)

            elif hasattr(torch.backends,"mps") and torch.backends.mps.is_available():
                gpu_avaliable = "Apple Silicon"
                vram_avaliable = "Unified"

            return {"message" : {"cpu" : cpu_cores, "ram" : ram_avaliable, "gpu_avaliable" : gpu_avaliable, "vram" : vram_avaliable}}
        
        except ConfigError as e:
            raise HTTPException(
                status_code=500,
                detail="Cannot fetch machine's hardware configuration"
            )
    
    def models(self):
        config = self.hardware()
        vram = config["message"]["vram"]

        if vram == None or vram == "Unified":
            return [
                    {"id": "openai-community/gpt2", "hugging_face_model_id": None, "max_completion_tokens": 1024, "publisher": "OpenAI", "type": "local","provider" : "hugging_face"},
                    {"id": "distilbert/distilgpt2", "hugging_face_model_id": None, "max_completion_tokens": 1024, "publisher": "HuggingFace", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen3-0.6B", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-0.5B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-Coder-0.5B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-0.5B", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "facebook/opt-125m", "hugging_face_model_id": None, "max_completion_tokens": 2048, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "hugging_face_model_id": None, "max_completion_tokens": 4096, "publisher": "TinyLlama", "type": "local","provider" : "hugging_face"},
                    {"id": "microsoft/Phi-3-mini-4k-instruct", "hugging_face_model_id": None, "max_completion_tokens": 4096, "publisher": "Microsoft", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen3-1.7B", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"}
                    ]
        
        elif vram >= 0 and vram < 4:
            return [
                    {"id": "Qwen/Qwen2.5-3B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen3-4B-Instruct-2507", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-1.5B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "google/gemma-3-1b-it", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Google", "type": "local","provider" : "hugging_face"},
                    {"id": "meta-llama/Llama-3.2-1B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "meta-llama/Llama-3.2-1B", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "microsoft/Phi-3-mini-4k-instruct", "hugging_face_model_id": None, "max_completion_tokens": 4096, "publisher": "Microsoft", "type": "local","provider" : "hugging_face"},
                    {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "hugging_face_model_id": None, "max_completion_tokens": 4096, "publisher": "TinyLlama", "type": "local","provider" : "hugging_face"},
                    {"id": "second-state/stablelm-2-zephyr-1.6b-GGUF", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Stability AI", "type": "local","provider" : "hugging_face"},
                    {"id": "EleutherAI/gpt-j-6b", "hugging_face_model_id": None, "max_completion_tokens": 2048, "publisher": "EleutherAI", "type": "local","provider" : "hugging_face"}
                    ]
        
        elif vram >= 4 and vram < 8:
            return [
                    {"id": "meta-llama/Llama-3.1-8B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-7B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen3-8B", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "mistralai/Mistral-7B-Instruct-v0.2", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Mistral AI", "type": "local","provider" : "hugging_face"},
                    {"id": "microsoft/Phi-3-mini-4k-instruct", "hugging_face_model_id": None, "max_completion_tokens": 4096, "publisher": "Microsoft", "type": "local","provider" : "hugging_face"},
                    {"id": "openai/gpt-oss-20b", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "OpenAI", "type": "local","provider" : "hugging_face"},
                    {"id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "DeepSeek", "type": "local","provider" : "hugging_face"},
                    {"id": "EleutherAI/gpt-j-6b", "hugging_face_model_id": None, "max_completion_tokens": 2048, "publisher": "EleutherAI", "type": "local","provider" : "hugging_face"}
                ]
        
        elif vram >=8 and vram<16:
            return [
                    {"id": "Qwen/Qwen2.5-3B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-7B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen3-8B", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "mistralai/Mistral-7B-Instruct-v0.3", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Mistral AI", "type": "local","provider" : "hugging_face"},
                    {"id": "01-ai/Yi-1.5-9B-Chat", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "01.AI", "type": "local","provider" : "hugging_face"},
                    {"id": "openai/gpt-oss-20b", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "OpenAI", "type": "local","provider" : "hugging_face"},
                    {"id": "microsoft/Phi-3-medium-8k-instruct", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Microsoft", "type": "local","provider" : "hugging_face"},
                    {"id": "openchat/openchat-3.6", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "OpenChat", "type": "local","provider" : "hugging_face"}
                    ]

        elif vram >= 16 and vram < 32:
            return [
                    {"id": "meta-llama/Llama-3.1-70B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "mistralai/Mixtral-8x7B-Instruct-v0.1", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Mistral AI", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-32B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "01-ai/Yi-1.5-34B-Chat", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "01.AI", "type": "local","provider" : "hugging_face"},
                    {"id": "deepseek-ai/deepseek-coder-33b-instruct", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "DeepSeek", "type": "local","provider" : "hugging_face"},
                    {"id": "google/gemma-2-27b-it", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Google", "type": "local","provider" : "hugging_face"},
                    {"id": "openai/gpt-oss-120b", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "OpenAI", "type": "local","provider" : "hugging_face"}
                   ]
        
        elif vram > 32:
            return [
                    {"id": "meta-llama/Llama-3.1-405B", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "meta-llama/Llama-3.3-70B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "Meta", "type": "local","provider" : "hugging_face"},
                    {"id": "Qwen/Qwen2.5-72B-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Alibaba", "type": "local","provider" : "hugging_face"},
                    {"id": "mistralai/Mixtral-8x22B-Instruct-v0.1", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "Mistral AI", "type": "local","provider" : "hugging_face"},
                    {"id": "deepseek-ai/DeepSeek-V2-Chat", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "DeepSeek", "type": "local","provider" : "hugging_face"},
                    {"id": "01-ai/Yi-1.5-110B-Chat", "hugging_face_model_id": None, "max_completion_tokens": 16384, "publisher": "01.AI", "type": "local","provider" : "hugging_face"},
                    {"id": "tiiuae/falcon-180B-chat", "hugging_face_model_id": None, "max_completion_tokens": 8192, "publisher": "TII UAE", "type": "local","provider" : "hugging_face"},
                    {"id": "deepseek-ai/DeepSeek-Coder-V2-Instruct", "hugging_face_model_id": None, "max_completion_tokens": 32768, "publisher": "DeepSeek", "type": "local","provider" : "hugging_face"}
                   ]
        
        else:
            raise Exception("Invalid Configuration Error")
        
    def load_models(self):
        session = Session()
        models = self.models()
        for model in models:
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

        