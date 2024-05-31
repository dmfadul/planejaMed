from flask import Blueprint

dashboard_bp = Blueprint(
                        'dashboard',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/dashboard/static'
                        )


@dashboard_bp.route('/dashboard')
def dashboard():
    return 'Dashboard under construction...'