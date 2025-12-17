from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# from . import routes
from .endpoints import ads, dashboard, logs, alerts, settings, auth, sync, debug
