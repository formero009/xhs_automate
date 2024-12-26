from flask import Flask
from flask_cors import CORS
from app.api import image, note, prompt, translate, static, health, workflow
from app.extensions import db

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(image.bp)
    app.register_blueprint(note.bp)
    app.register_blueprint(prompt.bp)
    app.register_blueprint(translate.bp)
    app.register_blueprint(static.bp)
    app.register_blueprint(health.bp)
    app.register_blueprint(workflow.bp)

    return app