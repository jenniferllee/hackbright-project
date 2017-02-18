from model import connect_to_db, db, Drug
from server import app


def load_drugs():
    """Load drugs from product.csv into database."""

    print "Drugs"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Drug.query.delete()

    # Read u.user file and insert data
    for row in open("data/product.csv"):
        row = row.rstrip()
        row = row.split(",")
        drug_name = row[3]

        drug = Drug(drug_name=drug_name)

        # We need to add to the session or it won't ever be stored
        db.session.add(drug)

    # Once we're done, we should commit our work
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Create tables
    db.create_all()

    # Import different types of data
    load_drugs()
