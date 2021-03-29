import os

from flask import Flask
from flask_bootstrap import Bootstrap


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    Bootstrap(app)
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    from . import map, home, planning, schedule
    app.register_blueprint(map.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(planning.bp)
    app.register_blueprint(schedule.bp)
    return app
