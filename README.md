# serve-keyed-vector-locale

A mirco service ("API") to serve 2D locale views around a given token in an vector space ("word embedding"). Powered by [GenSim](https://radimrehurek.com/gensim/)'s [KeyedVectors](https://radimrehurek.com/gensim/models/keyedvectors.html). Hosting in production with [Dokku](https://github.com/dokku/dokku).

## Development

1. install with [Pipenv](https://github.com/pypa/pipenv)
2. create a folder `data` and put keyedvector models in it ('filename.model'). The filenames will be used later on as endpoints in the API
3. pipenv run python app.py
4. `curl localhost:5000/filename?q=test`

## Production

1. create Dokku app etc.
2. `dokku storage:mount the-app-name /home/some/folder:/data` and put models in that folder (see above)
3. `git push dokku`

## License

MIT.
