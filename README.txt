I will use this API: https://apilist.fun/api/the-cocktail-db which will allow users to search based on the name of the drink, the ingredients, or category of drink. They will also be able to view a full list of the drink, or just generate a random selection. 
	The schema might look something like this:

Tables

1. Users
   - `user_id` (Primary Key)
   - `username`
   - `email`
   - `password_hash` (for security)
   - Other user profile information (e.g., name, age, etc.)

2. Flavors
   - `flavor_id` (Primary Key)
   - `name` (e.g., sweet, sour, spicy, fruity, etc.)

3. Liquors
   - `liquor_id` (Primary Key)
   - `name` (e.g., vodka, rum, gin, whiskey, etc.)

4. Cocktails
   - `cocktail_id` (Primary Key)
   - `name`
   - `instructions` (how to make the cocktail)
   - `image_url` (URL to an image of the cocktail)
   - Other cocktail details (e.g., glass type, garnish, etc.)

5. Ingredients
   - `ingredient_id` (Primary Key)
   - `name` (e.g., lime juice, simple syrup, soda, etc.)

6. Dietary Restrictions
   - `restriction_id` (Primary Key)
   - `name` (e.g., vegetarian, vegan, gluten-free, etc.)

7. User Dietary Restrictions
    - `user_id` (Foreign Key to Users)
    - `restriction_id` (Foreign Key to DietaryRestrictions)

Relationships

 A User can have multiple Dietary Restrictions (many-to-many relationship with UserDietaryRestrictions).
 A Cocktail can have multiple Ingredients, Flavors, and Liquors (many-to-many relationships with CocktailIngredients, CocktailFlavors, and CocktailLiquors).
A Cocktail can be associated with multiple Users who like it or have saved it as a favorite (many-to-many relationship not explicitly shown in the schema).


	Potential issues would be handling invalid search terms or dietary restrictions and of course the overall reliability of the API and things like rate limiting, changes to the API, cost of use, etc. There is sensitive information in this project, regarding a user’s login credentials, as well as their personal preferences and dietary restrictions. 
	The user flow and functionality would look something like 
1. User Registration and Login:
   - Users arrive at the website and can choose to either register for an account or log in if they already have one.

2. User Profile Setup:
   - After registration or login, users can set up their profile, providing information such as their name, email, and other optional details.
   - Users can also input their flavor and liquor preferences and select dietary restrictions from predefined options.

3. Home Page:
   - Users are directed to the home page after registration/login, where they can see featured cocktails, search for cocktails, or explore categories.

4. Search and Filtering:
   - Users can initiate a search for cocktails based on their preferences.
   - Users can filter cocktails by selecting specific flavors, liquors, or dietary restrictions.

5. Cocktail Listings:
   - The website fetches cocktail data from the CocktailDB API based on the user's preferences and displays a list of matching cocktails.
   - Each cocktail is represented with a name, image, and brief description.

6. Cocktail Details:
   - Users can click on a cocktail to view its detailed page, which includes ingredients, instructions, and additional information.
   - Users can save a cocktail to their favorites or mark it as "liked."

7. User Interaction:
   - Users can interact with the website by saving cocktails, liking them, or leaving reviews.
   - Users can also share cocktail recipes on social media if desired.

8. User Profile Management:
   - Users can access and edit their profiles at any time to update their preferences, change their profile picture, or modify their account settings.

9. Logout:
   - Users can log out of their accounts when they are done using the website.

10. Error Handling:
    - The website includes error handling to address issues like failed API requests, unavailable cocktails, or incorrect user input.

11. Recommendations:
Personalized cocktail recommendations based on user preferences and past interactions.
Featured or trending cocktails for discovery.
Algorithms that suggest cocktails similar to those the user has liked.
