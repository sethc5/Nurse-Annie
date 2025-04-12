from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Nurse Annie API is running!"})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    return jsonify({"summary": f"This is a placeholder summary for: {query}"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


def fetch_pubmed_abstracts(query, max_results=1):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    r = requests.get(base_url, params=params)
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    abstracts = []

    for pmid in ids:
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "text",
            "rettype": "abstract"
        }
        res = requests.get(fetch_url, params=fetch_params)
        abstracts.append(res.text.strip())

    return abstracts

def summarize_with_openai(text):
    prompt = f"""You are a warm, friendly health coach explaining medical research to someone aged 60+ who may be scared, confused, or overwhelmed.

Please read the following medical abstract and explain it in a calm, reassuring tone. Your job is to:
1. Tell them in a few sentences what this study found — as if you're sitting with them in a waiting room.
2. Explain why it matters for someone with type 2 diabetes, using everyday language (no technical terms).
3. Reassure them about what they can do today — simple actions or next steps they might ask their doctor about.

Please avoid clinical jargon. Do not mention “cross-sectional”, “cohort”, or “statistical significance.” Instead, talk about what this means for real people.

Here’s the abstract:

{text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful medical explainer for older adults."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.4
    )
    return response.choices[0].message["content"].strip()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


