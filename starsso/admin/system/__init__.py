from flask import Blueprint

# for avoid same name ;)
bp = Blueprint('systemd', __name__, url_prefix='/system')
