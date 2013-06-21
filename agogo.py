from flask import Flask
from flask import render_template

import utils

app = Flask(__name__)


@app.route("/s/<phrase>")
def search(phrase):
    db = utils.get_connection()
    hits = db.command("text", "subtitles", search=phrase)['results']
    results = [{
        "score": hit['score'],
        "subtitle": hit['obj'],
        "timestamp": int(hit['obj']['from']) - 10,
        "episode": db.files.find_one({'_id': hit['obj']['file']}),
    } for hit in hits]
    return render_template('search_results.html', results=results, search_term=phrase)

if __name__ == "__main__":
    app.run()
