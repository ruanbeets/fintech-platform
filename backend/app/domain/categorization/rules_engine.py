RULES = {
    "Food": ["restaurant", "burger", "pizza", "kfc", "mcdonalds"],
    "Transport": ["uber", "bolt", "fuel", "shell", "petrol"],
    "Groceries": ["spar", "pick n pay", "woolworths", "checkers"],
    "Entertainment": ["netflix", "spotify", "cinema"],
}


def categorize(description):

    if not description:
        return None

    desc = description.lower()

    for category, keywords in RULES.items():

        for keyword in keywords:

            if keyword in desc:
                return category

    return "Other"