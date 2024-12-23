from whoosh.index import open_dir

# Funktion zur Überprüfung des Index-Inhalts
def check_index_content(index_dir):
    try:
        # Öffne den Whoosh-Index
        ix = open_dir(index_dir)
        
        print("\n=== Index Overview ===")
        print(f"Index directory: {index_dir}")
        print(f"Stored fields: {ix.schema.names()}")
        
        with ix.searcher() as searcher:
            doc_count = searcher.doc_count()
            print(f"Total documents: {doc_count}\n")

            # Zeige die ersten 5 Dokumente im Index an
            print("=== Sample Documents (first 5) ===")
            for docnum, fields in enumerate(searcher.all_stored_fields()):
                print(f"Document {docnum + 1}: {fields}\n")
                if docnum >= 4:  # Begrenze auf 5 Dokumente
                    break

    except Exception as e:
        print(f"Error while checking the index: {str(e)}")

if __name__ == "__main__":
    index_dir = input("Enter the path to the Whoosh index directory: ").strip()
    if not index_dir:
        print("No index directory provided. Exiting.")
    else:
        check_index_content(index_dir)

from whoosh.index import open_dir

def validate_index(index_dir):
    try:
        ix = open_dir(index_dir)
        print("Index is valid and contains the following fields:")
        print(ix.schema.names())
    except Exception as e:
        print(f"Error validating index: {e}")

validate_index("path_to_your_index")


'''
# Häufigste 10 Wörter in den Dokumenten
from whoosh.index import open_dir
from whoosh.query import Every
from whoosh.analysis import StandardAnalyzer
from collections import Counter

# Funktion zur Extraktion der häufigsten Wörter
def extract_common_words(index_dir, num_words=10):
    try:
        # Öffne den Whoosh-Index
        ix = open_dir(index_dir)
        
        common_words = Counter()
        analyzer = StandardAnalyzer()
        
        with ix.searcher() as searcher:
            # Durchsuche alle Dokumente
            for docnum in searcher.documents():
                doc = searcher.stored_fields(docnum)
                content = doc.get("content", "")
                # Analysiere den Inhalt und zähle die Wörter
                tokens = [token.text for token in analyzer(content)]
                common_words.update(tokens)

        print(f"\n=== Top {num_words} Common Words ===")
        for word, count in common_words.most_common(num_words):
            print(f"{word}: {count}")

    except Exception as e:
        print(f"Error while extracting common words: {str(e)}")
'''