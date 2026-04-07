from app import app,db
from database.models import User  
from werkzeug.security import generate_password_hash

def initdb():
    with app.app_context():
        db.create_all() 

        # Check if admin is seeded or not
        admin = User.query.filter_by(username='admin').first() 

        if not admin: 
            # Hashed using sha256 , as default is slower and not that secure.
            hpassword = generate_password_hash('admin@iitm', method='pbkdf2:sha256')
            new_admin = User(
                username='admin', 
                hashedpassword=hpassword, 
                role='admin',
                status=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Database and Admmin created successfully.")
        else:
            print("Database already initialized.")

# seeding the db : for testing purposes
def setup():
    print('Seeding with initial values')  
    from database import setup 


if __name__ == '__main__':
    print("Resetting the db")
    initdb()
    setup()
    print('Setup complete')
    