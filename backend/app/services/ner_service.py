from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from app.config import settings


def get_client() -> TextAnalyticsClient:
    return TextAnalyticsClient(
        endpoint=settings.azure_language_endpoint,
        credential=AzureKeyCredential(settings.azure_language_key),
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
