from flask import Blueprint

privilege_bp = Blueprint('privilege',
                         __name__,
                         template_folder='templates',
                         static_folder='static',
                         static_url_path='/static/privilege'
                         )


@privilege_bp.route('/privilege')
def privilege():
    return 'privilege'
