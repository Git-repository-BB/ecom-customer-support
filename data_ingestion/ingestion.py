import os
from langchain_astradb import AstraDBVectorStore
import pandas as pd
from dotenv import load_dotenv
from typing import List, Tuple
from langchain_core.documents import Document
from openai import OpenAI

from utils.config_loader import load_config
from config.config_loader import load_config
from utils.model_loader_bb import ModelLoader


class DataIngestion:
    """
    Class to handle data transformation and ingestion into AstraDB vector store.
    """

    def __init__(self):
        """
        Initialize environment variables, embedding model, and set CSV file path.
        """
        print("Initializing DataIngestion pipeline...")
               
        self.model_loader=ModelLoader()
        self._load_env_variables()
        self.csv_path = self._get_csv_path()
        self.product_data = self._load_csv()
        self.config=load_config()
        


    def _get_csv_path(self):
        """
        Get path to the CSV file located inside 'data' folder.
        """
        print("Getting CSV file path...")
        current_dir = os.getcwd()
        print(f"Current working directory: {current_dir}")
        csv_path = os.path.join(current_dir, 'data', 'flipkart_product_review.csv')
        print(f"Constructed CSV path: {csv_path}")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        return csv_path
    
    def _load_csv(self):
        """
        Load product data from CSV.
        """
        print("Loading CSV file...")
        df = pd.read_csv(self.csv_path)
        expected_columns = {'product_title', 'rating', 'summary', 'review'}

        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns: {expected_columns}")
        
        print(f"CSV loaded successfully with columns: {df.columns}")
        print(df.head())  # Print the first few rows of the DataFrame for verification
        return df
    
    def _load_env_variables(self):
        """
        Load and validate required environment variables.
        """
        load_dotenv()
        
        required_vars = ["OPENAI_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
        
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")
    
    def transform_data(self):
        """
        Transform product data into a list of tuples for ingestion.
        Each tuple contains (product_title, rating, summary, review).
        """
        print("Transforming data...")
        product_list = []

        for _, row in self.product_data.iterrows():
            product_entry = {
                "product_name": row['product_title'],
                "product_rating": row['rating'],
                "product_summary": row['summary'],
                "product_review": row['review']
            }
            product_list.append(product_entry)

        print(f"Transformed product list: {product_list[:5]}")  # Print the first few entries for verification

        documents = []
        for entry in product_list:
            metadata = {
                "product_name": entry["product_name"],
                "product_rating": entry["product_rating"],
                "product_summary": entry["product_summary"]
            }
            doc = Document(page_content=entry["product_review"], metadata=metadata)
            documents.append(doc)
        
        print(f"Transformed documents: {documents[:5]}")  # Print the first few Document objects for verification    

        print(f"Transformed {len(documents)} documents.")
        return documents
    
    def store_in_vector_db(self, documents: List[Document]):
        """
        Store documents into AstraDB vector store.
        """
        collection_name=self.config["astra_db"]["collection_name"]
        vstore = AstraDBVectorStore(
            embedding= self.model_loader.load_embeddings(),
            collection_name=collection_name,
            api_endpoint=self.db_api_endpoint,
            token=self.db_application_token,
            namespace=self.db_keyspace,
        )

        inserted_ids = vstore.add_documents(documents)
        print(f"Successfully inserted {len(inserted_ids)} documents into AstraDB.")
        return vstore, inserted_ids
    
    def run_pipeline(self):
        """
        Run the full data ingestion pipeline: transform data and store into vector DB.
        """
        documents = self.transform_data()
        vstore, inserted_ids = self.store_in_vector_db(documents)

        # Optionally do a quick search
        query = "Can you tell me the low budget headphone?"
        results = vstore.similarity_search(query)

        print(f"\nSample search results for query: '{query}'")
        for res in results:
            print(f"Content: {res.page_content}\nMetadata: {res.metadata}\n")



if __name__ == "__main__":
    try:
        data_ingestion = DataIngestion()
        print("DataIngestion pipeline initialized successfully.")
        data_ingestion.run_pipeline()
        
    except Exception as e:
        print(f"Error initializing DataIngestion pipeline: {e}")
    print("End of DataIngestion class definition.")