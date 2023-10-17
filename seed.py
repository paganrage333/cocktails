from app import db 
from models import User, Cocktail, Likes

db.drop_all()
db.create_all()
