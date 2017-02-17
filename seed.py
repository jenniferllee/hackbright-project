from model import connect_to_db, db
from server import app


if __name__ == "__main__":
    connect_to_db(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Create tables
    db.create_all()
