import json
import os
import time

import pandas as pd
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# Catégories Azure AI Language pertinentes pour les skills
SKILL_CATEGORIES = {"Skill", "Product", "PersonType"}

# Score de confiance minimum
MIN_CONFIDENCE = 0.75

# Mots-clés tech en enrichissement
TECH_SKILLS = {
    "python", "r", "sql", "java", "scala", "julia",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "spark", "pyspark", "hadoop", "kafka",
    "airflow", "dbt", "databricks", "snowflake",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "azure", "aws", "gcp", "docker", "kubernetes",
    "git", "linux", "bash", "terraform",
    "tableau", "power bi", "powerbi", "looker",
    "fastapi", "flask", "django",
}


def get_client() -> TextAnalyticsClient:
    """Initialise le client Azure AI Language."""
    endpoint = os.getenv("ENDPOINT")
    key = os.getenv("API_KEY")

    if not endpoint or not key:
        raise ValueError(
            "\n❌ Variables manquantes dans .env :\n"
            "   AZURE_LANGUAGE_ENDPOINT\n"
            "   AZURE_LANGUAGE_KEY\n"
        )

    print(f"✅ Azure AI Language connecté : {endpoint}")
    return TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


def extract_skills_azure( client: TextAnalyticsClient, texts: list[str], batch_size: int = 5, sleep_sec: float = 0.5,):
    """
    Envoie les descriptions par batch à Azure AI Language.
    Enrichit avec mots-clés tech en fallback.

    Returns:
        Liste de JSON strings ex: '["Python", "SQL", "Azure"]'
    """
    results = []
    total = len(texts)

    for i in range(0, total, batch_size):
        batch = texts[i: i + batch_size]

        # Préparer documents (max 5120 chars par doc)
        documents = [
            {"id": str(j), "text": text[:5120], "language": "en"}
            for j, text in enumerate(batch)
        ]

        try:
            response = client.recognize_entities(documents=documents)

            for doc_idx, doc in enumerate(response):
                skills = set()

                if not doc.is_error:
                    # Entités Azure filtrées par catégorie + confiance
                    azure_skills = [
                        ent.text.strip()
                        for ent in doc.entities
                        if ent.category in SKILL_CATEGORIES
                        and ent.confidence_score >= MIN_CONFIDENCE
                        and 2 <= len(ent.text.strip()) <= 40
                    ]
                    skills.update(azure_skills)
                else:
                    print(f"  ⚠️  Erreur doc {i+doc_idx} : {doc.error}")

                # Enrichissement mots-clés tech
                text_lower = batch[doc_idx].lower()
                for keyword in TECH_SKILLS:
                    if keyword in text_lower:
                        label = keyword.upper() if len(keyword) <= 3 else keyword.title()
                        skills.add(label)

                results.append(json.dumps(sorted(skills)))

        except Exception as e:
            print(f" Erreur batch {i} : {e}")
            # Fallback : mots-clés uniquement pour ce batch
            for text in batch:
                skills = set()
                text_lower = text.lower()
                for keyword in TECH_SKILLS:
                    if keyword in text_lower:
                        label = keyword.upper() if len(keyword) <= 3 else keyword.title()
                        skills.add(label)
                results.append(json.dumps(sorted(skills)))

        # Progression
        done = min(i + batch_size, total)
        print(f" {done}/{total} traitées", end="\r")

        # Pause anti-throttling Azure
        if i + batch_size < total:
            time.sleep(sleep_sec)

    print()
    return results


def run( input_csv: str = "backend/data/processed/jobs_cleaned.csv", output_csv: str ="backend/data/processed/jobs_with_skills.csv", ):
    """Pipeline NER Azure complet."""
    
    print("  NER AZURE — Extraction des compétences")

    # Charger le CSV
    df = pd.read_csv(input_csv)
    print(f" {len(df)} offres chargées depuis : {input_csv}")

    # Connecter Azure
    client = get_client()

    # Extraction
    print("\n Envoi à Azure AI Language (batch=5)...")
    start = time.time()
    skills_list = extract_skills_azure(client, df["Job Description"].fillna("").tolist())   
    elapsed = time.time() - start

    df["skills_extracted"] = skills_list

    # Stats
    all_skills = [s for row in skills_list for s in json.loads(row)]
    print("\n=== RÉSULTATS ===")
    print(f"  Durée totale          : {elapsed:.1f}s")
    print(f"  Total skills extraits : {len(all_skills)}")
    print(f"  Moyenne par offre     : {len(all_skills)/len(df):.1f}")
    print(f"  Offres sans skills    : {(df['skills_extracted'] == '[]').sum()}")

    # Top 10
    from collections import Counter
    top = Counter(all_skills).most_common(10)
    print("\n  Top 10 compétences :")
    for skill, count in top:
        bar = "█" * int(count / max(c for _, c in top) * 20)
        print(f"    {skill:<20} {bar} {count}")

    # Sauvegarder
    df.to_csv(output_csv, index=False)
    print(f"\n Sauvegardé : {output_csv}")
    print("=" * 55)


if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else "backend/data/processed/jobs_cleaned.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else "backend/data/processed/jobs_with_skills.csv"
    run(inp, out)