from flask import Flask, render_template, redirect, session, request, g, flash, abort, url_for
from models import connect_db, db, get_cocktail_data, User, Cocktail, get_ingredient_data, get_cocktail_by_name, Like, create_cocktail_from_api
from sqlalchemy.exc import IntegrityError
import requests, json
from forms import UserAddForm, UserEditForm, LoginForm, CocktailForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cdqlhnwl:hdyss7l2CN1ZpEKwdxM_9T9iCiPJpFqN@heffalump.db.elephantsql.com/cdqlhnwl'
app.config['SECRET_KEY'] = 'tingaling155'
app.app_context().push()

connect_db(app)

db.drop_all()
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

    print("id type", type(drink_id))  # Print id type

    user_id = g.user.id

    try:
        # Fetch drink data from the API
        api_url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.RequestException as e:
        # Handle request errors
        flash("Error fetching drink details from the API", "danger")
        return redirect("/")

    print("####API DATA###", api_data)
    
    # Convert drink_id to a string before using it in the query
    drink_id = str(drink_id)

    create_cocktail_from_api(drink_id)

    # Check if a like with the same user_id and drink_id already exists
    existing_like = Like.query.filter_by(user_id=user_id, drink_id=drink_id).first()

    if existing_like:
        # Like already exists, you can update or handle it as needed
        flash("You have already liked this drink.", "warning")
    else:
        # Like doesn't exist, add a new like
        like = Like(user_id=user_id, drink_id=drink_id)
        db.session.add(like)
        db.session.commit()
        flash("You have liked this drink.", "success")

    return redirect("/")


# @app.route('/users/add_like/<string:drink_id>', methods=['POST'])
# def user_add_like(drink_id):

#     liked_drink = Cocktail.query.get_or_404(drink_id)

#     print("drink", drink_id)

#     return redirect("/", liked_drink=liked_drink)

@app.route('/liked_drinks', methods=['GET'])
def liked_drinks():
    """Display liked drinks for the currently logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = g.user.id

    liked_drinks = Like.query.filter_by(user_id=user_id).all()
    drink_ids = [liked.drink_id for liked in liked_drinks]

    drinks = [Cocktail.query.get(drink_id) for drink_id in drink_ids]

    return render_template("liked_drinks.html", liked_drinks=liked_drinks)

######## HOMEPAGE ########

@app.route("/", methods=["GET", "POST"])
def homepage():
    response = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")

    if response.status_code == 200:
        data = response.json()
        drink = data['drinks'][0]  # Get the first drink from the response

        create_cocktail_from_api(drink['idDrink'])
    else:
        drink = None

    return render_template("index.html", drink=drink)
    

@app.route("/search", methods=["GET", "POST"])
def search_form():
    form = CocktailForm()

    liquor_preference = form.liquor_preference.data
    cocktail_data = get_cocktail_data(liquor_preference)

    if cocktail_data:
            return render_template("results.html", cocktails=cocktail_data["drinks"])
    
    return render_template("searchform.html", form=form)

    # if form.validate_on_submit():
    #     liquor_preference = form.liquor_preference.data

    #     if liquor_preference:
    #         # Search by liquor preference
    #         cocktail_data = get_cocktail_data(liquor_preference)
        
    #     else:
    #         # Handle invalid form data
    #         return "Invalid form data"
        
    #     if cocktail_data:
    #         return render_template("results.html", cocktails=cocktail_data["drinks"])
    #     else:
    #         return "Error fetching cocktail data from API"
        
    # return render_template("searchform.html", form=form)

@app.route("/othersearch", methods=["GET", "POST"])
def ingredient_search():
    form = CocktailForm()

    ingredient = form.ingredient.data
    cocktail_data = get_ingredient_data(ingredient)
    
    print(cocktail_data)

    if cocktail_data:
            return render_template("results.html", cocktails=cocktail_data["drinks"])
        
    return render_template("searchform2.html", form=form)

@app.route("/namesearch", methods=["GET", "POST"])
def name_search():
    form = CocktailForm()

    if request.method == "POST":
        search_term = form.search_term.data
        cocktail_data = get_cocktail_by_name(search_term)

        if cocktail_data:
            return render_template("results.html", cocktails=cocktail_data["drinks"])
        
    return render_template("searchform3.html", form=form)

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



    

