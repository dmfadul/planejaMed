import migration_funcs
from app.models import User, Center
from app import create_app


# migration_funcs.add_centers()
# migration_funcs.migrate_users()
migration_funcs.migrate_base("CCQ--BASE")

# app = create_app()
# with app.app_context():
#     print(User.get_crm("Nikolas Kim"))
