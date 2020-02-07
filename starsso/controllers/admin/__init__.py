from ....utils import EnhancedBlueprint
from .system import bp as system_bp
from .user import bp as user_bp

bp = EnhancedBlueprint('admin', __name__, url_prefix='/admin')
bp.register_blueprint(system_bp)
bp.register_blueprint(user_bp)
