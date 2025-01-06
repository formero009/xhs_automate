from flask import Flask
from flask_cors import CORS
from app.api import image, note, prompt, translate, static, health, workflow, user, agent
from app.scheduler import scheduler
from app.models.agent import Agent, AgentStatus

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
    app.register_blueprint(user.bp)
    app.register_blueprint(agent.bp)

    # Initialize running agents
    # with app.app_context():
    #     running_agents = Agent.query.filter_by(status=AgentStatus.RUNNING).all()
    #     for agent1 in running_agents:
    #         scheduler.schedule_agent(agent1)

    return app