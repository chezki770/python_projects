import argparse
import random
import json

def load_word_list(file_path):
    """Load the word list from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            word_list = json.load(file)
            if 'words' not in word_list or not isinstance(word_list['words'], list):
                raise ValueError("Invalid JSON format: 'words' key missing or not a list.")
            return word_list
    except FileNotFoundError:
        print("The specified file was not found.")
        exit(1)
    except json.JSONDecodeError:
        print("The file does not contain valid JSON.")
        exit(1)
    except ValueError as e:
        print(e)
        exit(1)

def get_random_word(word_list):
    """Select a random word and its hint from the word list."""
    random_index = random.randint(0, len(word_list['words']) - 1)
    word_info = word_list['words'][random_index]
    return word_info['word'], word_info['hint'], random_index

def display_covered_word(word):
    """Return the covered word string."""
    return "_ " * len(word)

def update_covered_word(guessed_letter, random_word, covered_word):
    """Update the covered word with the guessed letter if it exists in the random word."""
    score = 0
    new_covered_word = list(covered_word.replace(" ", ""))
    for index, letter in enumerate(random_word):
        if letter == guessed_letter:
            new_covered_word[index] = guessed_letter
            score += 1
    return " ".join(new_covered_word), score

def get_valid_input():
    """Prompt the user for a valid letter input."""
    while True:
        ui = input("What letter do you think it is? ")
        if len(ui) == 1 and (ui.isalpha() or ui == "."):
            return ui.lower()

def initialize_players(number_of_players):
    """Initialize player names and scores."""
    players = []
    for i in range(number_of_players):
        name = input(f"Enter the name of player number {i + 1}: ")
        players.append({'name': name, 'score': 0})
    return players

def play_turn(player, random_word, covered_word, tried_letters):
    """Handle the logic for a single player's turn."""
    print(f"Hint: {random_word['hint']}")
    print(f"Word: {covered_word}")
    print(f"{player['name']}, it's your turn.")
    
    user_input = get_valid_input()
    if user_input == ".":
        return False, covered_word, 0

    if user_input in tried_letters:
        print("You've already tried that letter. Try again.")
        return True, covered_word, 0

    tried_letters.add(user_input)

    if user_input in random_word['word']:
        covered_word, score = update_covered_word(user_input, random_word['word'], covered_word)
        print(f"{player['name']}, your score is: {player['score'] + score}")
        return True, covered_word, score
    else:
        print("The letter is not in the word.")
        return True, covered_word, 0

def main():
    parser = argparse.ArgumentParser(description="Play a word guessing game.")
    parser.add_argument("file_path", type=str, help="Path to the JSON file with word list and hints")
    parser.add_argument("number_of_players", type=int, help="Number of players")
    args = parser.parse_args()

    word_list = load_word_list(args.file_path)
    players = initialize_players(args.number_of_players)
    game_running = True

    while word_list['words'] and game_running:
        word, hint, word_index = get_random_word(word_list)
        covered_word = display_covered_word(word)
        tried_letters = set()

        while "_" in covered_word.replace(" ", "") and game_running:
            for player in players:
                game_running, covered_word, score = play_turn(player, {'word': word, 'hint': hint}, covered_word, tried_letters)
                player['score'] += score
                if not game_running or "_" not in covered_word.replace(" ", ""):
                    break

        word_list['words'].pop(word_index)

    for player in players:
        print(f"{player['name']}, your final score is: {player['score']}")

if __name__ == "__main__":
    main()

