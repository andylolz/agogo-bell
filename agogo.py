from flask import Flask, redirect, render_template, request, url_for

import utils

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/search")
def search():
    q = request.args.get('q', '')
    if q == '':
        return redirect(url_for('home'))
    db = utils.get_connection()
    hits = db.command("text", "subtitles", search=q)['results']
    results = [{
        "score": hit['score'],
        "subtitle": hit['obj'],
        "timestamp": max(0, int(hit['obj']['from']) - 10),  # rewind about 10 seconds
        "episode": db.files.find_one({'_id': hit['obj']['file']}),
    } for hit in hits]
    return render_template('search_results.html', results=results, search_term=q)


# @app.route("/s/<phrase>/")

if __name__ == "__main__":
    app.run()
