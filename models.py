from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests

bcrypt = Bcrypt()
db = SQLAlchemy()


def get_cocktail_data(liquor_preference):
    base_url = "https://www.thecocktaildb.com/api/json/v1/1/filter.php"

    params = {
        "i": liquor_preference
    }

    print("API Request URL:", base_url)
    print("API Request Parameters:", params)

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        print("API Response:", data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except ValueError as e:
        print(f"JSON Decoding Error: {e}")
        return None

def get_ingredient_data(ingredient):
    base_url = "https://www.thecocktaildb.com/api/json/v1/1/filter.php"

    params = {
        "i": ingredient
    }

    print("API Request URL:", base_url)
    print("API Request Parameters:", params)

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        print("API Response:", data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except ValueError as e:
        print(f"JSON Decoding Error: {e}")
        return None
    
def get_cocktail_by_name(search_term):
    base_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={search_term}"

    params = {
        "s": search_term
    }

    print("API Request URL:", base_url)
    print("API Request Parameters:", params)

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        print("API Response:", data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except ValueError as e:
        print(f"JSON Decoding Error: {e}")
        return None

class Cocktail(db.Model):
    """Cocktail data model."""

    __tablename__ = 'cocktails'

    id = db.Column(
        db.String,
        primary_key=True
    )

    strDrink = db.Column(
        db.Text,
        nullable=False
    )

    strCategory = db.Column(
        db.Text
    )

    strInstructions = db.Column(
        db.Text
    )

    likes = db.relationship('Likes', back_populates='cocktail')

    liked_by_users = db.relationship('User', secondary='likes', back_populates='liked_cocktails', overlaps="likes")

    def __repr__(self):
        return f"<Cocktail {self.strDrink}>"
    

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/REPLACE"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    likes = db.relationship(
        'Likes',
        back_populates='user',
        overlaps="liked_by_users"
    )

    liked_cocktails = db.relationship('Cocktail', secondary='likes', back_populates='liked_by_users', overlaps="likes")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    
class Likes(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    cocktail_id = db.Column(
        db.String,
        db.ForeignKey('cocktails.id', ondelete='cascade'),
    )

    user = db.relationship('User', back_populates='likes', overlaps="liked_by_users,liked_cocktails")
    cocktail = db.relationship('Cocktail', back_populates='likes', overlaps="liked_by_users,liked_cocktails")

def connect_db(app):
    db.app = app
    db.init_app(app)