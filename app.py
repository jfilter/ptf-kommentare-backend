from os import environ
from pathlib import Path

from flask import Flask, jsonify, request
from gensim.models import KeyedVectors
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DEBUG = not "FILTER_PRODUCTION" in environ

data_dir = "data" if DEBUG else "/data"

vecs = {}
for m in Path(data_dir).glob("*.model"):
    vecs[m.stem] = KeyedVectors.load(str(m), mmap="r")


@app.route("/<vec_name>")
def index(vec_name):
    q, n = request.args.get("q"), request.args.get("n", 10, type=int)
    v = vecs[vec_name]
    results = v.most_similar(q, topn=n)
    tokens, _ = [q] + list(zip(*results))
    vectors = [v[t] for t in tokens]
    vectors = PCA(n_components=2).fit_transform(vectors)
    vectors = MinMaxScaler((-1, 1)).fit_transform(vectors)
    return jsonify({"tokens": tokens, "vectors": vectors.tolist()})


if __name__ == "__main__":
    app.run(debug=DEBUG)
