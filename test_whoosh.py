from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.scoring import FunctionWeighting

# Funktion zur Validierung des Index
# Überprüft, ob der Index korrekt geladen werden kann und gibt eine Übersicht der Felder aus
def validate_index(index_dir):
    try:
        ix = open_dir(index_dir)
        print("\n=== Index Overview ===")
        print(f"Index directory: {index_dir}")
        print(f"Stored fields: {ix.schema.names()}")
    except Exception as e:
        print(f"Error validating index: {e}")

# Funktion zur Überprüfung des Inhalts des Index
# Zeigt die Anzahl der Dokumente und die ersten 5 Einträge an
def check_index_content(index_dir):
    try:
        ix = open_dir(index_dir)

        with ix.searcher() as searcher:
            doc_count = searcher.doc_count()
            print(f"Total documents: {doc_count}\n")

            # Zeige die ersten 5 Dokumente an
            print("=== Sample Documents (first 5) ===")
            for docnum, fields in enumerate(searcher.all_stored_fields()):
                print(f"Document {docnum + 1}: {fields}\n")
                print('****************************************************')
                if docnum >= 4:  # Zeigt maximal 5 Einträge an
                    break

    except Exception as e:
        print(f"Error while checking the index: {str(e)}")

# Benutzerdefinierte Bewertungsfunktion (Scoring)
# Beeinflusst das Ranking der Suchergebnisse basierend auf benutzerdefinierten Kriterien
# Kombinierte Scoring-Funktion
def combined_score_fn(searcher, fieldname, text, matcher):
    # Termfrequenz (TF)
    term_freq = matcher.value_as("frequency")
    
    # Inverse Dokumentenhäufigkeit (IDF)
    idf = searcher.idf(fieldname, text)
    
    # Position des ersten Auftretens
    positions = matcher.value_as("positions")
    position_score = 1 / (min(positions) + 1) if positions else 1  # Je früher, desto besser
    
    # Gesamtgewichtung
    proximity_weight = 1.5  # Verstärkung für nahe Terme
    position_weight = 2.0   # Verstärkung für Position
    idf_weight = 1.0        # Gewichtung für IDF
    
    return (
        term_freq +
        idf_weight * idf +
        position_weight * position_score +
        proximity_weight * term_freq / (1 + len(positions))
    )

# Scoring-Objekt erstellen
my_combined_weighting = FunctionWeighting(combined_score_fn)

# Suche mit kombinierter Scoring-Methode
def perform_combined_search(index_dir, query_text):
    ix = open_dir(index_dir)
    with ix.searcher(weighting=my_combined_weighting) as searcher:
        parser = QueryParser("content", ix.schema)
        myquery = parser.parse(query_text)
        results = searcher.search(myquery, limit=10)
        
        print(f"=== Combined Search Results for Query: '{query_text}' ===")
        for result in results:
            print(f"File Name: {result['file_name']}")
            print(f"Score: {result.score}")
            print(f"Snippet: {result.highlights('content')}\n")

# Hauptprogramm
if __name__ == "__main__":
    index_dir = input("Enter the path to the Whoosh index directory: ").strip()
    if not index_dir:
        print("No index directory provided. Exiting.")
    else:
        validate_index(index_dir)
        check_index_content(index_dir)

        query_text = input("Enter your search query: ").strip()
        if query_text:
            perform_combined_search(index_dir, query_text)
