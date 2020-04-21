import random
import re
from os import environ
from pathlib import Path
import requests

from flask_caching import Cache
from flask import Flask, jsonify, request
from flask_cors import CORS
from gensim.models import KeyedVectors
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
CORS(app)

DEBUG = not "FILTER_PRODUCTION" in environ

data_dir = "data" if DEBUG else "/data"

if DEBUG:
    app.config["CACHE_TYPE"] = "null"
else:
    app.config["CACHE_TYPE"] = "redis"
    app.config["CACHE_REDIS_URL"] = environ["REDIS_URL"]
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60 * 60 * 24 * 14  # 2 weeks

cache = Cache(app)

vecs = {}
for m in Path(data_dir).glob("*.model"):
    vecs[m.stem] = KeyedVectors.load(str(m), mmap="r")

@app.route("/typeahead/<vec_name>")
@cache.cached(query_string=True)
def typeahead(vec_name):
    q = request.args.get("q", type=str)

    if q == '':
        return jsonify({"tokens": []})

    v = vecs[vec_name]

    q = re.sub(r"\d+", "0", q)
    q = q.lower()

    tokens = [t for t in v.index2entity if t.startswith(q)]
    tokens = sorted(tokens, key=len)
    return jsonify({"tokens": tokens[:10]})

# make sure to check wheter file exists
@app.route("/vectors/typeahead_videos/<vec_name>")
@cache.cached(query_string=True)
def typeahead_videos(vec_name):
    q = request.args.get("q", type=str)

    if q == '':
        return jsonify({"tokens": []})

    v = vecs[vec_name]

    q = re.sub(r"\d+", "0", q)
    q = q.lower()

    tokens = [t for t in v.index2entity if t.startswith(q)]
    tokens = sorted(tokens, key=len)
    results = []
    for t in tokens:
        if len(results) >= 10:
            break
        r = requests.head('http://kommentare.vis.one/videos/' + t + '.mp4')
        if r.ok:
            results.append(t)
    return jsonify({"tokens": results})


@app.route("/vectors/nearest/<vec_name>")
@cache.cached(query_string=True)
def nearest(vec_name):
    q, n = request.args.get("q"), request.args.get("n", 10, type=int)
    if q == '':
        return jsonify({"tokens": [], "vectors": []})

    v = vecs[vec_name]
    results = v.most_similar(q, topn=n)
    tokens, _ = list(zip(*results))
    tokens = [q] + list(tokens)
    vectors = [v[t] for t in tokens]
    vectors = PCA(n_components=2).fit_transform(vectors)
    vectors = MinMaxScaler((-1, 1)).fit_transform(vectors)
    return jsonify({"tokens": tokens, "vectors": vectors.tolist()})


@app.route("/vectors/dist/<vec_name>")
@cache.cached(query_string=True)
def dist(vec_name):
    tokens = request.args.getlist("q")
    v = vecs[vec_name]
    vectors = [v[t] for t in tokens]
    vectors = PCA(n_components=2).fit_transform(vectors)
    vectors = MinMaxScaler((-1, 1)).fit_transform(vectors)
    return jsonify({"tokens": tokens, "vectors": vectors.tolist()})


@app.route("/vectors/sim/<vec_name>")
@cache.cached(query_string=True)
def sim(vec_name):
    """get similarities
    """
    q, n = request.args.get("q"), request.args.get("n", 10, type=int)
    v = vecs[vec_name]
    results = v.most_similar(q, topn=n)
    return jsonify({"tokens": [r[0] for r in results], "sims": [r[1] for r in results]})


@app.route("/vectors/sim_multiple/<vec_name>")
@cache.cached(query_string=True)
def sim_multiple(vec_name):
    """get similarities
    """
    qs = request.args.getlist("q")
    v = vecs[vec_name]
    return jsonify({"tokens": qs, "sims": [v.similarity(qs[0], x) for x in qs[1:]]})


@app.route("/vectors/sim_random/<vec_name>")
@cache.cached(query_string=True)
def sim_random(vec_name):
    """get similarities, n random tokens
    """
    q, n = request.args.get("q"), request.args.get("n", 10, type=int)
    v = vecs[vec_name]
    tokens = [q] + random.sample(v.index2entity, n)
    return jsonify({"tokens": tokens, "sims": [v.similarity(q, x) for x in tokens[1:]]})


@app.route("/vectors/token_random/<vec_name>")
@cache.cached(query_string=True, timeout=10) # 10 seconds
def random_tokens(vec_name):
    n = request.args.get("n", 100, type=int)
    v = vecs[vec_name]
    tokens = random.sample(v.index2entity, n)
    return jsonify({"tokens": tokens})


if __name__ == "__main__":
    app.run(debug=DEBUG)
