"""Route alignment module.

This module imports grouped route files so the application has one place to
see all route domains and their shared blueprint wiring.
"""

from app.routes.common import api_bp
from app.routes import auth, connections, core, moderation, notifications, profile

blueprints = [api_bp]
