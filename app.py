from flask import Flask, render_template, redirect, session, request, g, flash
from models import connect_db, db, get_cocktail_data, User
from sqlalchemy.exc import IntegrityError
import requests
from forms import UserAddForm, UserEditForm, LoginForm, CocktailForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cocktails'
app.config['SECRET_KEY'] = 'colada'
app.app_context().push()

connect_db(app)
db.create_all()

############# SIGN UP / LOGIN / LOGOUT ROUTES ############

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


######## HOMEPAGE ########

@app.route("/", methods=["GET", "POST"])
def homepage():
    response = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")

    if response.status_code == 200:
        data = response.json()
        drink = data['drinks'][0]  # Get the first drink from the response
    else:
        drink = None

    return render_template("index.html", drink=drink)
    

@app.route("/search", methods=["GET", "POST"])
def search_form():
    form = CocktailForm()

    if form.validate_on_submit():
        # Flask-WTF has validated the form, and you can access the form data using form.field_name.data
        liquor_preference = form.liquor_preference.data

         # Call the function to get cocktail data
        cocktail_data = get_cocktail_data(liquor_preference)
        
        if cocktail_data:
            # Render the template with the cocktail data
            return render_template("results.html", cocktails=cocktail_data["drinks"])
        else:
            # Handle API request error
            return "Error fetching cocktail data from API"
        
    return render_template("searchform.html", form=form)

@app.route("/results", methods=["GET"])
def results():
    # Fetch the cocktail data (you may need to modify this logic)
    flavor_preference = request.args.get("flavor_preference")
    liquor_preference = request.args.get("liquor_preference")
    dietary_restrictions = request.args.getlist("dietary_restrictions")
    
    cocktail_data = get_cocktail_data(flavor_preference, liquor_preference, dietary_restrictions)
    
    if cocktail_data:
        return render_template("results.html", cocktails=cocktail_data["drinks"])
    else:
        return "Error fetching cocktail data from API"

