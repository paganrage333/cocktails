from flask import Flask, render_template, redirect, session, request, g, flash, abort, url_for
from models import connect_db, db, get_cocktail_data, User, Cocktail
from sqlalchemy.exc import IntegrityError
import requests
from forms import UserAddForm, UserEditForm, LoginForm, CocktailForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cocktails'
app.config['SECRET_KEY'] = 'colada'
app.app_context().push()

connect_db(app)

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

######## USER ROUTES #########
@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    likes = [drink.id for drink in user.likes]
    return render_template('users/show.html', user=user, likes=likes)

@app.route('/users/<int:user_id>/likes', methods=["GET"])
def show_likes(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/likes.html', user=user, likes=user.likes)

@app.route('/drinks/<string:drink_id>/like', methods=['POST'])
def add_like(drink_id):
    """Toggle a liked drink for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    # Debug: Print drink_id to check its value
    print("drink_id:", drink_id)

    liked_drink = Cocktail.query.get_or_404(drink_id)

    # Debug: Print liked_drink details to check if it exists
    print("liked_drink:", liked_drink)

    liked_drink = Cocktail.query.get_or_404(drink_id)

    user_likes = g.user.likes

    if liked_drink in user_likes:
        g.user.likes = [like for like in user_likes if like != liked_drink]
    else:
        g.user.likes.append(liked_drink)

    db.session.commit()

    return redirect("/")

@app.route('/users/add_like/<string:drink_id>', methods=['POST'])
def user_add_like(drink_id):
    """Toggle a liked drink for the currently-logged-in user."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    # Debug: Print drink_id to check its value
    print("drink_id:", drink_id)

    print("id type", type(drink_id)) #print id type
    

    # # Debug: Print liked_drink details to check if it exists
    # print("liked_drink:", liked_drink)

    try:
        liked_drink = Cocktail.query.get_or_404(drink_id)  

    except Exception as e:
        print("######", e)
    
    user_likes = g.user.likes

    if liked_drink in user_likes:
        # User already liked this drink, so unlike it
        g.user.likes = [like for like in user_likes if like != liked_drink]
    else:
        # User hasn't liked this drink, so add it to their likes
        g.user.likes.append(liked_drink)

    db.session.commit()

    return redirect("/")  # Redirect to the appropriate page after liking/unliking

@app.route('/users/add_like/', methods=['POST'])
def please_god():
    return redirect("/")

@app.route('/liked_drinks', methods=['GET'])
def liked_drinks():
    """Display liked drinks for the currently logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Fetch the liked drinks for the user
    liked_drinks = g.user.liked_cocktails

    return render_template("liked_drinks.html", liked_drinks=liked_drinks)

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
        liquor_preference = form.liquor_preference.data

        if liquor_preference:
            # Search by liquor preference
            cocktail_data = get_cocktail_data(liquor_preference)
        
        else:
            # Handle invalid form data
            return "Invalid form data"
        
        if cocktail_data:
            return render_template("results.html", cocktails=cocktail_data["drinks"])
        else:
            return "Error fetching cocktail data from API"
        
    return render_template("searchform.html", form=form)

@app.route("/results", methods=["GET"])
def results():
    # Fetch the cocktail data
    liquor_preference = request.args.get("liquor_preference")
    
    cocktail_data = get_cocktail_data(liquor_preference)
    
    if cocktail_data:
        return render_template("results.html", cocktails=cocktail_data["drinks"])
    else:
        return "Error fetching cocktail data from API"
    

@app.route("/drink/<string:drink_id>")
def drink_details(drink_id):
    api_url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Check for request errors
        data = response.json()
    except requests.exceptions.RequestException as e:
        # Handle request errors, e.g., network issues or API problems
        return render_template('error.html', message=f"Error: {str(e)}")
    except requests.exceptions.JSONDecodeError as e:
        # Handle JSON decoding errors (e.g., empty response)
        return render_template('error.html', message="Error decoding API response")

    if "drinks" in data:
        drink = data["drinks"][0]  # Assuming the API returns details for a single drink
        return render_template('drink_details.html', drink=drink, drink_id=drink_id)
    else:
        return render_template('error.html', message="No data available for this drink")



    

