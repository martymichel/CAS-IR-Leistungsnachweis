from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

app = Flask(__name__)

class WhooshSearchEngine:
    def __init__(self, index_dir):
        self.ix = open_dir(index_dir)

    def search(self, query, top_k=10):
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema)
            myquery = parser.parse(query)
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
                    "create_date": result.get("create_date", "Unknown")
                })
            return output

index_dir = r"C:\Users\s.mueller\GitHub\CAS-IR-Leistungsnachweis\whoosh_index"
search_engine = WhooshSearchEngine(index_dir)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    if not query:
        return render_template("index.html", error="Bitte Suchbegriff eintragen.")

    results = search_engine.search(query)
    if not results:
        return render_template("index.html", error="Keine Ergebnisse gefunden.")

    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
