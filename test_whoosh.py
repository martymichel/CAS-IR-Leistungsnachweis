from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.scoring import FunctionWeighting

# Function to validate the index
# Checks if the index can be loaded correctly and provides an overview of the fields
def validate_index(index_dir):
    try:
        ix = open_dir(index_dir)
        print("\n=== Index Overview ===")
        print(f"Index directory: {index_dir}")
        print(f"Stored fields: {ix.schema.names()}")
    except Exception as e:
        print(f"Error validating index: {e}")

# Function to inspect the content of the index
# Displays the number of documents and the first 5 entries
def check_index_content(index_dir):
    try:
        ix = open_dir(index_dir)

        with ix.searcher() as searcher:
            doc_count = searcher.doc_count()
            print(f"Total documents: {doc_count}\n")

            # Display the first 5 documents
            print("=== Sample Documents (first 5) ===")
            for docnum, fields in enumerate(searcher.all_stored_fields()):
                print(f"Document {docnum + 1}: {fields}\n")
                print('****************************************************')
                if docnum >= 4:  # Show a maximum of 5 entries
                    break

    except Exception as e:
        print(f"Error while checking the index: {str(e)}")

# Custom scoring function
# Influences the ranking of search results based on custom criteria
# Combined scoring function
def combined_score_fn(searcher, fieldname, text, matcher):
    # Term frequency (TF)
    term_freq = matcher.value_as("frequency")
    
    # Inverse document frequency (IDF)
    idf = searcher.idf(fieldname, text)
    
    # Position of the first occurrence
    positions = matcher.value_as("positions")
    position_score = 1 / (min(positions) + 1) if positions else 1  # Earlier is better
    
    # Total weighting
    proximity_weight = 1.5  # Boost for nearby terms
    position_weight = 2.0   # Boost for position
    idf_weight = 1.0        # Weighting for IDF
    
    return (
        term_freq +
        idf_weight * idf +
        position_weight * position_score +
        proximity_weight * term_freq / (1 + len(positions))
    )

# Create scoring objects
my_combined_weighting = FunctionWeighting(combined_score_fn)

# Search with combined scoring method
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

# Main Program
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
