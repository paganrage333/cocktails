from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself')
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class CocktailForm(FlaskForm):
    liquor_preference = SelectField('Liquor Preference', choices=[('gin', 'Gin'), ('vodka', 'Vodka'), ('rum', 'Rum'), ('whiskey', 'Whiskey')])
    ingredient = StringField('Ingredient', validators=[DataRequired()])
    search_term = StringField('Search Term', validators=[DataRequired()])
    submit = SubmitField('Search Cocktails')