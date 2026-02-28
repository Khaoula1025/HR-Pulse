from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv('API_KEY')
ENDPOINT = os.getenv('ENDPOINT')


def get_client() -> TextAnalyticsClient:
    return TextAnalyticsClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(API_KEY),
    )


def extract_skills(text: str) -> list[str]:
    client = get_client()
    response = client.recognize_entities([text])
    skills = [
        entity.text
        for doc in response
        if not doc.is_error
        for entity in doc.entities
        if entity.category in ("Skill", "Product", "Other")
    ]
    return list(set(skills))
