from whoosh.index import open_dir

# function to validate the index
def validate_index(index_dir):
    try:
        ix = open_dir(index_dir)
        print("\n=== Index Overview ===")
        print(f"Index directory: {index_dir}")
        print(f"Stored fields: {ix.schema.names()}")
    except Exception as e:
        print(f"Error validating index: {e}")

# function to check content of created index
def check_index_content(index_dir):
    try:
        # open whoosh index
        ix = open_dir(index_dir)
        
        with ix.searcher() as searcher:
            doc_count = searcher.doc_count()
            print(f"Total documents: {doc_count}\n")

            # show first 5 entries of index
            print("=== Sample Documents (first 5) ===")
            for docnum, fields in enumerate(searcher.all_stored_fields()):
                print(f"Document {docnum + 1}: {fields}\n")
                print('****************************************************')
                if docnum >= 4: # change amount of shown entries if needed
                    break

    except Exception as e:
        print(f"Error while checking the index: {str(e)}")

# main program
if __name__ == "__main__":
    index_dir = input("Enter the path to the Whoosh index directory: ").strip()
    if not index_dir:
        print("No index directory provided. Exiting.")
    else:
        validate_index(index_dir)
        check_index_content(index_dir)