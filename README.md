# cjworkbench
A visual dataflow programming system for journalists. More at on the [public server](blog.cjworkbench.org)!


To set up a development environment:

- Requires Python 3.5 or greater
- Install (virtualenv)[http://docs.python-guide.org/en/latest/dev/virtualenvs/]
- Install (npm)[https://www.npmjs.com/]
- git clone this repo with submodules: `git clone --recursive https://github.com/jstray/cjworkbench.git`
- `pip install -r requirements.txt` to install Python packages
- `pip install -r requirements-dev.txt` to install packages required for development
- `npm install` to install JavaScript packages
- `python manage.py migrate` to initialize the database
- `python manage.py createsuperuser` if you ever want to login to Django admin (you do)

If you get a message about missing Chartbuilder (probably when running webpack), check that there are files in /chartbuilder/chartbuilder and /chartbuilder/chartbuilder-ui. You may have missed the `--recursive` above when cloning. Fix that with `git submodule update --init --recursive`

To run:
- `python manage.py runserver` to start the Django server. It will automatically recompile any .py file you edit.
- browse to `127.0.0.1:8000/api/initmodules` to load module definitions (needed on first run, or when modules changed)

At the moment the home page `127.0.0.1:8000` does nothing. Go to `127.0.0.1:8000/workflows` to list available workflows.

To develop:
- `./node_modules/.bin/webpack --config webpack.config.js --watch` to compile JS and CSS whenever changed
- `python manage.py test` for back end tests
- `npm test` for front end tests
