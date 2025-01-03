from flask import Flask, render_template, request, jsonify
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.scoring import FunctionWeighting
from whoosh import highlight
import json
import os

# define environment for web app (Flask)
app = Flask(__name__)

# Path for storing settings
SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    # Default settings
    return {
        "proximity_weight": 1.0,
        "position_weight": 0.8,
        "idf_weight": 0.6
    }

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# Custom scoring function
class CustomScoring(FunctionWeighting):
    def __init__(self, settings):
        self.settings = settings
        super().__init__(self.custom_score)

    def custom_score(self, searcher, fieldname, text, matcher):
        # Get term frequency
        term_freq = matcher.value_as("frequency")
        
        # Get IDF score
        idf = searcher.idf(fieldname, text)
        
        # Get positions and calculate position score
        positions = matcher.value_as("positions")
        if positions:
            # Normalize position score based on document length
            doc_length = searcher.doc_field_length(matcher.id(), fieldname)
            position_score = 1.0 - (min(positions) / doc_length)
        else:
            position_score = 0.0

        # Calculate proximity score based on term positions
        if positions and len(positions) > 1:
            # Calculate average distance between consecutive positions
            distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            avg_distance = sum(distances) / len(distances)
            proximity_score = 1.0 / (1.0 + avg_distance)
        else:
            proximity_score = 0.0

        # Apply weights and combine scores
        weighted_score = (
            term_freq +
            (self.settings["idf_weight"] * idf) +
            (self.settings["position_weight"] * position_score) +
            (self.settings["proximity_weight"] * proximity_score)
        )

        return weighted_score

# search engine function
class WhooshSearchEngine:
    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.ix = open_dir(index_dir)
        self.settings = load_settings()

    def update_settings(self, new_settings):
        self.settings = new_settings.copy()
        save_settings(self.settings)

    def search(self, query, top_k=10):
        scorer = CustomScoring(self.settings)
        
        # Configure highlighting
        fragmenter = highlight.ContextFragmenter(maxchars=300, surround=75)
        formatter = highlight.HtmlFormatter(tagname="mark", classname="match")
        highlighter = highlight.Highlighter(fragmenter=fragmenter, formatter=formatter)
        
        with self.ix.searcher(weighting=scorer) as searcher:
            parser = QueryParser("content", self.ix.schema)
            myquery = parser.parse(query)
            results = searcher.search(myquery, limit=top_k, terms=True)
            
            output = []
            for result in results:
                content = result["content"]
                snippets = highlighter.highlight_hit(result, "content")
                output.append({
                    "file_name": result["file_name"],
                    "path": result["path"].replace('/', '\\'),
                    "page": result["page"],
                    "score": round(result.score, 3),
                    "snippet": snippets,
                    "author": result.get("author", "Unknown"),
                    "create_date": result.get("create_date", "Unknown")
                })
            return output

# declaration of index path
index_dir = r".\whoosh_index"
search_engine = WhooshSearchEngine(index_dir)

@app.route("/")
def home():
    return render_template("index.html", settings=search_engine.settings)

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    if not query:
        return render_template("index.html", error="Bitte Suchbegriff eintragen.", settings=search_engine.settings)

    results = search_engine.search(query)
    if not results:
        return render_template("index.html", error="Keine Ergebnisse gefunden.", settings=search_engine.settings)

    return render_template("index.html", results=results, query=query, settings=search_engine.settings)

@app.route("/update_settings", methods=["POST"])
def update_settings():
    try:
        new_settings = {
            "proximity_weight": float(request.form.get("proximity_weight", 1.5)),
            "position_weight": float(request.form.get("position_weight", 2.0)),
            "idf_weight": float(request.form.get("idf_weight", 1.0))
        }
        search_engine.update_settings(new_settings)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# main program -> start web app
if __name__ == "__main__":
    app.run(debug=True)