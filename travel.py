"""
Travel Destination Selection Program

Program uses simple logic and data in the form of a .csv file to match a users preferences (input) to a recommended location.
"""

__author__ = "Richard Roth"
__date__ = "20190505"


from destinations import Destinations

# Input provided to the question generators including sub-options
CONTINENT_INPUT = ("Which continents would you like to travel to?",
                   ["Asia", "Africa", "North America", "South America", "Europe", "Oceania", "Antarctica"])

COST_INPUT = ("What is money to you?",
              [('$$$', 'No object'),
                  ('$$', 'Spendable, so long as I get value from doing so'),
                  ('$', 'Extremely important; I want to spend as little as possible')])

CRIME_INPUT = ("How much crime is acceptable when you travel?",
               ['Low', 'Average', 'High'])

CHILDREN_INPUT = ("Will you be travelling with children?",
                  ["Yes", "No"])

SEASON_INPUT = ("Which seasons do you plan to travel in?",
                ['Spring', 'Summer', 'Autumn', 'Winter'])

CLIMATE_INPUT = ("What climate do you prefer?",
                 ["Cold", "Cool", "Moderate", "Warm", "Hot"])

QUESTIONS = [
    ('continent', CONTINENT_INPUT, 'multiple_numeric'),
    ('cost', COST_INPUT, 'string'),
    ('crime', CRIME_INPUT, 'numeric'),
    ('kids', CHILDREN_INPUT, 'numeric'),
    ('season', SEASON_INPUT, 'multiple_numeric'),
    ('climate', CLIMATE_INPUT, 'numeric')
]

INTEREST_INPUT = [
    ['sports', 'sports'],
    ['wildlife', 'wildlife'],
    ['nature', 'nature'],
    ['historical', 'historical sites'],
    ['cuisine', 'fine dining'],
    ['adventure', 'adventure activities'],
    ['beach', 'the beach'],
]


def basic_input(gen_input, options):
    """Generates questions and sub-options.

    Parameters:
        question (str): Text of the question to be displayed.
        options (list[tuple(str,str)]): List of the answer options, where first value is the selection and second value is the option

    Return:
        (str) Value entered by user
    """
    print(gen_input)
    print_questions = {key: print(f"  {key}) {option}")
                       for key, option in options}
    return input('> ')


def input_numeric_options(gen_input, options):
    """Generates questions for numeric options and includes an invalid input handler.

    Parameters:
        question (str): Text of the question to be displayed.
        options (list[str]): List of the answer options

    Return:
        (str) Option selected by user.
    """
    while True:
        response = basic_input(gen_input, enumerate(options, start=1))
        try:
            response = int(response)
            if 1 <= response <= len(options):
                return options[response - 1]
        except (ValueError, IndexError):
            pass
        print(f"\nError: {response} is not a valid input.",
              "Try again.\n")


def input_str_options(gen_input, options):
    """Generates questions for string options, included invalid input handler.

    Parameters:
        question (str): Text of the question to be displayed.
        options (list[tuple(str,str)]): List of the answer options, where first value is selection and second value is option

    Return:
        (str) Option selected.
    """
    valid_responses = {key for key, _ in options}
    while True:
        response = basic_input(gen_input, options)
        if response in valid_responses:
            return response
        print(f"\nError: {response} is not a valid.",
              "Try again.\n")


def input_multiple_numeric_options(gen_input, options):
    """Generates questions for multiple numeric options. Includes invalid input handler. Users can enter multiple inputs.

    Parameters:
        question (str): Text of the question to be displayed.
        options (list[str]): List of the answer options

    Return:
        (list[str]) Options selected.
    """
    while True:
        response = basic_input(gen_input, enumerate(options, start=1))
        responses = []
        try:
            for option in response.split(','):
                option = int(option)
                assert 1 <= option <= len(options)
                responses.append(options[option - 1])
        except (ValueError, IndexError, AssertionError):
            print(f"\nError: {response} is not a valid.",
                  "Try again.\n")
        else:
            return responses


def input_interest_question(label):
    """Generates interest questions.

    Parameters:
        label (str): Text describing the activity.

    Return:
        (int) Level of interest indicated by the user.
    """
    while True:
        print(f"How much do you like {label}? (-5 to 5)")
        response = input('> ')
        try:
            response = int(response)
            if -5 <= response <= 5:
                return response
        except ValueError:
            pass
        print(f"\nError: {response} is not valid.",
              "Try again.\n")


def main():
    """Determine a possible destination for a user based on their interests."""
    print("Welcome to Travel Inspiration!\n")
    name = input("What is your name? ")
    print(f"\nHi, {name}!\n")

    # Task 1: Questions & Inputs
    # Prompts the user for their travel preferences and interests.
    responses = {}
    interests = {}

    # Decides how to get the input from the user
    for key, (question, options), type_ in QUESTIONS:
        if type_ == "numeric":
            responses[key] = input_numeric_options(question, options)
        elif type_ == "multiple_numeric":
            responses[key] = input_multiple_numeric_options(question,
                                                            options)
        elif type_ == "string":
            responses[key] = input_str_options(question, options)
        else:
            raise ValueError(f"Unknown question type: {type_}")
        print()

    print("Now we would like to ask you some questions about your interests, on "
          "a scale of -5 to 5. -5 indicates strong dislike, whereas 5 indicates "
          "strong interest, and 0 indicates indifference.\n")

    for key, label in INTEREST_INPUT:
        interests[key] = input_interest_question(label)
        print()

    # Selects the best matching destination based on the user's preferences.
    match = None    # Signal that no match has been found yet.

    # Tasks 2-6:
    for destination in Destinations().get_all():
        # If destination's continent, crime level, cost, kid friendliness, climate
        # does not match the user's preferences, will skip to the next destination.
        if destination.get_continent().title() not in responses['continent']:
            continue

        if (CRIME_INPUT[1].index(destination.get_crime().title())
                > CRIME_INPUT[1].index(responses['crime'])):
            continue

        if len(destination.get_cost()) > len(responses['cost']):
            continue

        if responses['kids'] == "Yes" and not destination.is_kid_friendly():
            continue

        # Task 3: Climate & Season Factor
        if responses['climate'].lower() != destination.get_climate():
            continue

        if match is None:
            match = destination
        else:
            # Task 6:
            # Based on the season factor, which season has the highest score.
            prev_score = max(match.get_season_factor(season.lower())
                             for season in responses['season'])
            score = max(destination.get_season_factor(season.lower())
                        for season in responses['season'])

            # Task 4: Interests
            prev_interest_score = sum(response * match.get_interest_score(key)
                                      for key, response in interests.items())
            interest_score = sum(response * destination.get_interest_score(key)
                                 for key, response in interests.items())

            prev_score *= prev_interest_score
            score *= interest_score

            if score > prev_score:
                match = destination

    print("Thank you for answering all our questions.",
          "Your next travel destination is:")
    if match is None:
        print(match)
    else:
        print(match.get_name())


if __name__ == "__main__":
    main()
