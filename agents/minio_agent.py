import db.minio as minio
from models.llm_client import LLMClient


class MinIOAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.session = minio.initialize_minio()

    def handle_question(self, question: str) -> str:
        """
        Placeholder for MinIO Agent query handling.

        Args:
            question (str): The user question.

        Returns:
            str: "Not Implemented"
        """
        return "Not Implemented"