from app import create_app, db
import migration.funcs as funcs
import json


funcs.migrate_base("CCQ--BASE")


# app = create_app()

# with app.app_context():
#     db.create_all()
#     # db.session.commit()
#     # print('Database created!')

#     pass