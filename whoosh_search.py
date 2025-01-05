from flask import Flask, render_template, request, jsonify
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, OrGroup
from whoosh.scoring import FunctionWeighting
from whoosh import highlight
import time
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
        "proximity_weight": 2.5,
        "position_weight": 1.5,
        "idf_weight": 1.2
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
        
        # POSITION SCORING
        # Get positions and calculate position score
        positions = matcher.value_as("positions")
        if positions:
            # Normalize position score based on document length
            doc_length = searcher.doc_field_length(matcher.id(), fieldname)
            # Rate position based on how close it is to the beginning of the document
            position_score = 1.0 - (min(positions) / doc_length)
        else:
            position_score = 0.0

        # PROXIMITY SCORING
        # Calculate proximity score based on term positions
        if positions and len(positions) > 1:
            # Calculate average distance between consecutive positions
            distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            avg_distance = sum(distances) / len(distances)
            # Rate proximity based on average distance between terms
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

    # Dynamic max quality calculation, based on the maximum values of each scoring component
    def max_quality(self, searcher, fieldname):
        terms = searcher.field_terms(fieldname)
        if not terms:
            return 0.0

        # Get maximum values for each scoring component
        max_term_freq = max(terms.values(), default=1)
        max_idf = max(searcher.idf(fieldname, term) for term in terms)
        max_position_score = 1.0
        max_proximity_score = 1.0

        return (
            max_term_freq +
            (self.settings["idf_weight"] * max_idf) +
            (self.settings["position_weight"] * max_position_score) +
            (self.settings["proximity_weight"] * max_proximity_score)
        )

# search engine function
class WhooshSearchEngine:
    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.ix = open_dir(index_dir)
        self.settings = load_settings()

    def update_settings(self, new_settings):
        self.settings = new_settings.copy()
        save_settings(self.settings)

    def get_top_results(self, results, top_k):
        # Track seen documents to ensure we get top_k unique documents
        seen_docs = set()
        top_results = []
        
        for result in results:
            file_name = result["file_name"]
            if file_name not in seen_docs:
                seen_docs.add(file_name)
                top_results.append(result)
                if len(top_results) >= top_k:
                    break
        return top_results

    def search(self, query, top_k=10):
        scorer = CustomScoring(self.settings)
        
        # Initialize metrics
        metrics = {
            "start_time": time.time(),
            "total_docs": 0,
            "results_count": 0
        }
        
        # Sanitize and prepare query
        query = query.strip()
        if not query:
            return [], metrics
        
        # Configure highlighting
        fragmenter = highlight.ContextFragmenter(maxchars=300, surround=75)
        formatter = highlight.HtmlFormatter(tagname="mark", classname="match")
        highlighter = highlight.Highlighter(fragmenter=fragmenter, formatter=formatter)
        
        with self.ix.searcher(weighting=scorer) as searcher:
            # Configure parser to handle phrases and multiple terms
            parser = QueryParser("content", self.ix.schema, group=OrGroup)
            
            # Get total documents in index
            metrics["total_docs"] = searcher.doc_count_all()
            
            # Handle multi-word queries by wrapping in quotes if not already quoted
            if " " in query and not (query.startswith('"') and query.endswith('"')):
                query = f'"{query}"'
                
            myquery = parser.parse(query)
            # Get more results initially to handle grouping
            results = searcher.search(myquery, limit=top_k * 3, terms=True)
            
            # Get total documents in index
            metrics["total_docs"] = searcher.doc_count_all()
            metrics["results_count"] = len(results)
            
            # Group results by document name
            grouped_results = {}
            for result in results:
                file_name = result["file_name"]
                if file_name not in grouped_results:
                    grouped_results[file_name] = {
                        "file_name": file_name,
                        "path": result["path"].replace('/', '\\'),
                        "pages": [result["page"]],
                        "score": result.score,
                        "snippet": highlighter.highlight_hit(result, "content"),
                        "author": result.get("author", "Unknown"),
                        "create_date": result.get("create_date", "Unknown")
                    }
                else:
                    # Only append page if not already present
                    if result["page"] not in grouped_results[file_name]["pages"]:
                        grouped_results[file_name]["pages"].append(result["page"])
                    # Update snippet and score only if this result has a higher score
                    if result.score > grouped_results[file_name]["score"]:
                        grouped_results[file_name]["score"] = result.score
                        grouped_results[file_name]["snippet"] = highlighter.highlight_hit(result, "content")
            
            # Sort pages within each group and format them
            output = []
            for doc in grouped_results.values():
                doc["pages"].sort()
                doc["page"] = ", ".join(map(str, doc["pages"]))
                # Remove extra whitespace from snippets
                doc["snippet"] = ' '.join(doc["snippet"].split())
                doc["score"] = round(doc["score"], 3)
                output.append(doc)
            
            # Sort by score descending
            output.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top_k unique documents
            output = output[:top_k]
            
            # Calculate search duration
            metrics["duration"] = round((time.time() - metrics["start_time"]) * 1000, 2)  # in milliseconds
            
            return output, metrics

# declaration of index path
index_dir = r".\whoosh_index"
search_engine = WhooshSearchEngine(index_dir)

# definition of template file for rendering output
@app.route("/")
def home():
    return render_template("index.html", settings=search_engine.settings)

# function to get search query and render results or error messages
@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    results_per_page = int(request.form.get("results_per_page", 10))
    
    if not query or not query.strip():
        return render_template("index.html", error="Bitte Suchbegriff eintragen.", settings=search_engine.settings)

    # Trim whitespace
    query = query.strip()
    results, metrics = search_engine.search(query, top_k=results_per_page)
    if not results:
        return render_template("index.html", error="Keine Ergebnisse gefunden.", settings=search_engine.settings)

    return render_template("index.html", results=results, query=query, settings=search_engine.settings, metrics=metrics)

# function to update scoring options in web app
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