from scripts.ingest import clean_title


def test_clean_title():
    assert clean_title("  Data   Scientist  ") == "Data Scientist"
