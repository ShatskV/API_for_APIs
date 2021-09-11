from db_model import db
import server
db.create_all(app=server)