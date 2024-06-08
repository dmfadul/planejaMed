import migration_funcs
from app.models import User, Center
from app import create_app
from app.models._funcs import unify_appointments


# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.migrate_base("CCG--BASE")

# app = create_app()
# with app.app_context():
#     print(User.get_crm("Nikolas Kim"))
