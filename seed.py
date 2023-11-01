from app import app
from models import User, Cocktail, Like, db

db.drop_all()
db.create_all()

Cocktail.query.delete()

margarita = Cocktail({
      "idDrink": "11007",
      "strDrink": "Margarita",
      "strTags": "IBA,ContemporaryClassic",
      "strCategory": "Ordinary Drink",
      "strIBA": "Contemporary Classics",
      "strAlcoholic": "Alcoholic",
      "strGlass": "Cocktail glass",
      "strInstructions": "Rub the rim of the glass with the lime slice to make the salt stick to it. Take care to moisten only the outer rim and sprinkle the salt on it. The salt should present to the lips of the imbiber and never mix into the cocktail. Shake the other ingredients with ice, then carefully pour into the glass.",
      "strInstructionsDE": "Reiben Sie den Rand des Glases mit der Limettenscheibe, damit das Salz daran haftet. Achten Sie darauf, dass nur der äußere Rand angefeuchtet wird und streuen Sie das Salz darauf. Das Salz sollte sich auf den Lippen des Genießers befinden und niemals in den Cocktail einmischen. Die anderen Zutaten mit Eis schütteln und vorsichtig in das Glas geben.",
      "strInstructionsIT": "Strofina il bordo del bicchiere con la fetta di lime per far aderire il sale.\r\nAvere cura di inumidire solo il bordo esterno e cospargere di sale.\r\nIl sale dovrebbe presentarsi alle labbra del bevitore e non mescolarsi mai al cocktail.\r\nShakerare gli altri ingredienti con ghiaccio, quindi versarli delicatamente nel bicchiere.",
      "strDrinkThumb": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg",
      "strIngredient1": "Tequila",
      "strIngredient2": "Triple sec",
      "strIngredient3": "Lime juice",
      "strIngredient4": "Salt",
      "strMeasure1": "1 1/2 oz ",
      "strMeasure2": "1/2 oz ",
      "strMeasure3": "1 oz ",
      "strImageSource": "https://commons.wikimedia.org/wiki/File:Klassiche_Margarita.jpg",
      "strImageAttribution": "Cocktailmarler",
      "strCreativeCommonsConfirmed": "Yes",
      "dateModified": "2015-08-18 14:42:59"
    })

db.session.add(margarita)

db.session.commit()