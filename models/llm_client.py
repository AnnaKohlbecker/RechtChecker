import requests
from huggingface_hub import InferenceClient
from config.settings import HF_API_TOKEN


class LLMClient:
    def __init__(self, api_key: str = HF_API_TOKEN):
        """
        Initialize the LLM client using the Hugging Face InferenceClient for Instruct models
        and requests for chat models.

        Args:
            api_key (str): The Hugging Face API key for authentication.
        """
        if not api_key:
            raise ValueError("HF_API_TOKEN must be provided or set in the environment variables.")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.instruct_client = InferenceClient(api_key=self.api_key)
        
    def query_instruct(self, model: str, messages: list, max_tokens: int = 500, temperature: float = 1.0) -> dict:
        """
        Query the LLM using the Instruct model for chat completion.

        Args:
            model (str): The name of the model to query.
            messages (list): A list of messages in the format [{"role": "user", "content": "..."}].
            max_tokens (int): The maximum number of tokens for the response.
            temperature (float): Sampling temperature for response generation.

        Returns:
            dict: The response from the API.
        """
        try:
            response = self.instruct_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Error querying the instruct model API: {e}")

    def query_chat(self, model_url: str, inputs: str, max_tokens: int = 500, temperature: float = 1.0) -> dict:
        """
        Query the LLM using the chat model.

        Args:
            model_url (str): The API URL for the chat model.
            inputs (str): The input text for the model.
            max_tokens (int): The maximum number of tokens for the response.
            temperature (float): Sampling temperature for response generation.

        Returns:
            dict: The response from the API.
        """
        payload = {
            "inputs": inputs,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature
            }
        }
        try:
            response = requests.post(model_url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad HTTP responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error querying the chat model API: {e}")