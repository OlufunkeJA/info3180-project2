from app.routes.common import api_bp

# Import route modules so their handlers register on the shared blueprint.
from app.routes import auth, connections, core, moderation, notifications, profile


def register_blueprints(app):
    """Register all route blueprints for the application."""
    app.register_blueprint(api_bp)
