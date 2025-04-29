from src.utils.tooling import tool

@tool
def classify_foods(food_list: list) -> str:
    """
    Classifies a list of foods into specific botanical categories.
    Args:
        food_list (list): A list of foods to classify.
    Returns:
        str: A string with categories as keys and lists of foods as values.
    """
    categories = {
        "fruits": [
            "apple", "banana", "orange", "grape", "strawberry", "plum", "peach", "pear",
            "cherry", "blueberry", "raspberry", "pineapple", "mango", "kiwi", "lemon",
            "lime", "watermelon", "cantaloupe", "avocado", "tomato", "cucumber", "bell pepper",
            "eggplant", "okra", "zucchini", "pumpkin", "olive"
        ],
        "vegetables": [
            "carrot", "broccoli", "spinach", "lettuce", "celery", "fresh basil", "sweet potato",
            "potato", "onion", "garlic", "cabbage", "kale", "cauliflower", "asparagus", "radish",
            "turnip", "beet", "artichoke", "brussels sprouts", "peas", "mushroom",
            "sweet potatoes",
        ],
        "grains": [
            "rice", "wheat", "oats", "barley", "quinoa", "corn", "rye", "millet", "sorghum",
            "buckwheat", "flour"
        ],
        "nuts": [
            "almond", "walnut", "cashew", "peanut", "hazelnut", "pecan", "pistachio", "macadamia",
            "brazil nut", "chestnut", "acorn"
        ],
        "legumes": [
            "lentil", "chickpea", "bean", "pea", "soybean", "black bean", "kidney bean", "pinto bean",
            "navy bean", "lima bean", "green beans",
        ],
        "other": [
            "milk", "eggs", "coffee", "Oreos", "allspice", "sugar", "salt", "honey", "maple syrup",
            "vinegar", "oil", "butter", "cheese", "yogurt", "cream", "meat", "fish", "poultry"
        ]
    }
    classified_foods = {category: [] for category in categories}

    for food in food_list:
        food_lower = food.lower()
        classified = False
        for category, examples in categories.items():
            if food_lower in examples:
                classified_foods[category].append(food)
                classified = True
                break
        if not classified:
            classified_foods.setdefault("unknown", []).append(food)

    #classified_foods["vegetables"].sort()

    result = []
    for category, foods in classified_foods.items():
        if foods:
            result.append(f"{category.capitalize()}: {', '.join(foods)}")

    return "Food classification:\n" + "\n".join(result)