from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser

# define environment for web app (Flask)
app = Flask(__name__)

# search engine function (extende with optional limitation of search within author-list)
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
    def search(self, query, author=None, top_k=10):  # limitation of result amount to 10
        with self.ix.searcher() as searcher:
            parser = MultifieldParser(["content", "author"], self.ix.schema)
            myquery = parser.parse(query)
            if author and author != "Alle":
                myquery = myquery & parser.parse(f"author:{author}")
            results = searcher.search(myquery, limit=top_k)
            output = []
            # create data for output in web app
            for result in results:
                output.append({
                    "file_name": result["file_name"],
                    "path": result["path"].replace('/', '\\'),  # replace \ with / to get consistent file paths
                    "page": result["page"],
                    "score": round(result.score, 2),
                    "snippet": result.highlights("content"),
                    "author": result.get("author", "Unknown"),
                    "create_date": result.get("create_date", "Unknown")
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
