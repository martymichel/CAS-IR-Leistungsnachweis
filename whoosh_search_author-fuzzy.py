from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import Term
from whoosh.query import FuzzyTerm

# define environment for web app (Flask)
app = Flask(__name__)

# search engine function (extended with fuzzy-search, search also in filename and score boosting for term in filename)
class WhooshSearchEngine:
    # open index
    def __init__(self, index_dir):
        self.ix = open_dir(index_dir)

    # get list of authors from the index
    def get_authors(self):
        with self.ix.searcher() as searcher:
            authors = set()
            for fields in searcher.all_stored_fields():
                author = fields.get("author", "Unknown")
                authors.add(author)
            return sorted(authors)

    # search function
    def search(self, query, author=None, top_k=10):
        with self.ix.searcher() as searcher:
            # Create a parser for "content" and "file_name", boosting "file_name" scoring
            parser = MultifieldParser(["content", "file_name"], self.ix.schema, fieldboosts={"file_name": 2.0, "content": 1.0})
            myquery = parser.parse(query)

            # Optional fuzzy query
            fuzzy_query = FuzzyTerm("content", query, maxdist=1)  # maxdist = maximal distance (1 or 2)
            myquery = myquery | fuzzy_query  # Combination of queries

            # Filter by author if specified
            if author and author != "Alle":
                author_filter = Term("author", author)
                myquery = myquery & author_filter
            
            results = searcher.search(myquery, limit=top_k)
            output = []
            for result in results:
                output.append({
                    "file_name": result["file_name"],
                    "path": result["path"].replace('/', '\\'),
                    "page": result["page"],
                    "score": round(result.score, 2),
                    "snippet": result.highlights("content"),
                    "author": result.get("author", "Unknown"),
                    "create_date": result.get("create_date", "Unknown"),
                })
            return output


# declaration of index path - make sure the correct path is configured
index_dir = r".\whoosh_index"
search_engine = WhooshSearchEngine(index_dir)

# define .html template for web app
@app.route("/")
def home():
    authors = search_engine.get_authors()
    return render_template("index_author.html", authors=authors)

# get search query(ies) and hand over to the search engine
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    selected_author = request.form.get("author")
    if not query:
        return render_template("index_author.html", error="Bitte Suchbegriff eintragen.", authors=search_engine.get_authors())

    results = search_engine.search(query, author=selected_author)
    if not results:
        return render_template("index_author.html", error="Keine Ergebnisse gefunden.", authors=search_engine.get_authors())

    return render_template("index_author.html", results=results, query=query, authors=search_engine.get_authors(), selected_author=selected_author)

# main program -> start web app (webserver will run on local instance on http://127.0.0.1:5000)
if __name__ == "__main__":
    app.run(debug=True)

# press Ctrl-C to interrupt
