from flask import Blueprint, render_template

calendar_bp = Blueprint(
                        'calendar',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/calendar'
                        )


@calendar_bp.route('/calendar/<center>', methods=['GET'])
def calendar(center):
    print(center)

    kwargs = {
    'month_name': "Enero",
    'month_year': 2023,
    'center': center,
    'calendar_days': [],
    'curr_user_schedule': []
    }
    return render_template("calendar.html", **kwargs)

