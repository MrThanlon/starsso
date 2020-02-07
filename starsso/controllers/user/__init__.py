from ....utils import EnhancedBlueprint
from .privilege import bp as privilege_bp

bp = EnhancedBlueprint('user', __name__, url_prefix='/user')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    pass


@bp.route('/register', methods=('GET', 'POST'))
def register():
    pass


@bp.route('/getVerify', methods=('GET', 'POST'))
def get_verify():
    pass


@bp.route('/modify', methods=('GET', 'POST'))
def modify():
    pass


bp.register_blueprint(privilege_bp)
