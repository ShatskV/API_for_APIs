from server import create_app, db
import config
# with app.app_context():
db.create_all(app=create_app())
# print(config.SQLALCHEMY_DATABASE_URI)
