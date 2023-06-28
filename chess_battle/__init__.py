import os
from flask import Flask, current_app
from .database import db
import click


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        # DATABASE=os.path.join(app.instance_path, "chess_battle.sqlite"),
        SQLALCHEMY_DATABASE_URI='sqlite:///' +
        os.path.join(app.instance_path, 'chess_battle_orm.db'),
        PRE_DEFINED_DATA=os.path.join(app.instance_path, "players.csv")
    )

    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Welcome to chess battle"
    # from . import auth
    from . import settings
    from . import player
    from . import battles

    # app.register_blueprint(auth.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(player.bp)

    app.register_blueprint(battles.bp)
    app.add_url_rule("/", endpoint="index")
    # with app.app_context():
    #     db.create_all()
    app.cli.add_command(init_db_command, 'init-db')
    return app


@click.command
def init_db_command():
    click.echo('sometext')
    """Clear the existing data and create new tables."""
    with current_app.app_context():
        db.create_all()
    click.echo("Initialized the database.")
