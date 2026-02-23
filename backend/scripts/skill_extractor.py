# script de ner cleaning et d'extraction d'entités pour les offres d'emploi
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os       
load_dotenv() 
endpoint = "https://westeurope.api.cognitive.microsoft.com/"
Api_key = os.getenv("API_KEY")


documents = [
    """
    Capgemini recrute un Développeur Python pour rejoindre son équipe à Casablanca.
    Vous travaillerez sur des projets cloud utilisant Azure et SQL Server.
    Une expérience de 3 ans en Django est souhaitée.
    Envoyez votre candidature à recrutement@capgemini.com
    """,
    """
    Deloitte recherche actuellement un Data Analyst basé à Rabat.
    Le candidat idéal est titulaire d’un Bac+5 en Data Science et maîtrise Power BI, Excel et SQL.
    Merci d’envoyer votre CV à hr@deloitte.com.
    """,
]


client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(Api_key))

response = client.recognize_entities(documents)

for doc in response:
    print("---- Nouvelle offre ----")
    for entity in doc.entities:
        print(f"Texte : {entity.text}")
        print(f"Type : {entity.category}")
        print(f"Sous-type : {entity.subcategory}")
        print(f"Score : {entity.confidence_score}")
        print("-----")
