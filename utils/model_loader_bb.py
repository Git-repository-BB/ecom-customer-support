import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

class ModelLoader:
    """
    A utility class to load embedding models and LLM models.
    """
    
    def __init__(self):
        print("Initializing ModelLoader...")
        load_dotenv()
        self._validate_env()
        self.config=load_config()
        print("Ending ModelLoader...")

    def _validate_env(self):
        """
        Validate necessary environment variables.
        """
        required_vars = ["OPENAI_API_KEY"]
        # Force clear old key if cached
        # if "GROQ_API_KEY" in os.environ:
        #     del os.environ["GROQ_API_KEY"]
        self.openai_api_key=os.getenv("OPENAI_API_KEY")
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")

    def load_embeddings(self):
        """
        Load and return the embedding model.
        """
        print("Loading Embedding model")
        model_name=self.config["embedding_model"]["model_name"]
        return OpenAIEmbeddings(model=model_name)

    def load_llm(self):
        """
        Load and return the LLM model.
        """
        print("LLM loading...")
        model_name=self.config["llm"]["model_name"]
        print(self.openai_api_key)
        openai_model=ChatOpenAI(model=model_name,openai_api_key=self.openai_api_key)
        #openai_model=ChatGoogleGenerativeAI(model=model_name)
        
        return openai_model  # Placeholder for future LLM loading