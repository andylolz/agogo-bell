from flask import Flask
from flask import render_template

from utils import db

app = Flask(__name__)


@app.route("/s/<word>")
def search(word):
    results = []
    hits = db.lookup.find({'word': word})
    for hit in hits:
        subtitle = db.subtitles.find({'_id': hit['subtitle']})[0]
        file_ = db.files.find({'_id': subtitle['file']})[0]
        result = {
            'filename': file_['filename'],
            'subtitle': subtitle['line'],
            'from': subtitle['from'],
            'to': subtitle['to'],
        }
        results.append(result)
    return render_template('search_results.html', results=results, search_term=word)

if __name__ == "__main__":
    app.run()
