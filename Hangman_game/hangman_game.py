import argparse
import random
import json

def load_word_list(file_path):
    try:
        with open(file_path, 'r') as file:
            word_list = json.load(file)
            return word_list
    except FileNotFoundError:
        print("The specified file was not found.")
        exit(1)
    except json.JSONDecodeError:
        print("The file does not contain valid JSON.")
        exit(1)

def random_num(word_list):
    return random.randint(0, len(word_list['words']) - 1)

def random_word(word_list, number):
    return list(word_list['words'][number]['word'])

def hint(word_list, number):
    return word_list['words'][number]['hint']

def covered_word_str(random_word):
    return "_ " * len(random_word)

def if_letter_in_word(guessed_letter, random_word, covered_word):
    score = 0
    new_covered_word = list(covered_word.replace(" ", ""))
    for index, letter in enumerate(random_word):
        if letter == guessed_letter:
            new_covered_word[index] = guessed_letter
            score += 1
    return " ".join(new_covered_word), score

def correct_input():
    while True:
        ui = input("What letter do you think it is? ")
        if len(ui) == 1 and (ui.isalpha() or ui == "."):
            return ui.lower()

def main():
    parser = argparse.ArgumentParser(description="Play a word guessing game.")
    parser.add_argument("file_path", type=str, help="Path to the JSON file with word list and hints")
    parser.add_argument("number_of_players", type=int, help="Number of players")
    args = parser.parse_args()

    word_list = load_word_list(args.file_path)
    if not word_list:
        print("Word list is empty or not loaded properly.")
        exit(1)
    
    words = word_list['words']

    number_of_players = args.number_of_players
    name_of_players_list = [None] * number_of_players
    score_of_players_list = [0] * number_of_players

    for i in range(number_of_players):
        name_of_players_list[i] = input(f"Enter the name of player number {i + 1}: ")

    turn_of_players = 0
    game_running = True

    while words and game_running:
        random_number = random_num(word_list)
        random_word_value = random_word(word_list, random_number)
        hint_of_random_word = hint(word_list, random_number)
        covered_word = covered_word_str(random_word_value)
        tried_letters = set()
        
        while "_" in covered_word.replace(" ", ""):
            turn_of_players = turn_of_players % number_of_players + 1
            print(hint_of_random_word)
            print(covered_word) 
            print(f"{name_of_players_list[turn_of_players - 1]}, your turn")
            
            user_input = correct_input()
            if user_input == ".":
                game_running = False
                break
            
            if user_input in tried_letters:
                print("You've already tried that letter. Try again.")
                turn_of_players -= 1
                continue
            else:
                tried_letters.add(user_input)
            
            if user_input in random_word_value:
                covered_word, score = if_letter_in_word(user_input, random_word_value, covered_word)
                score_of_players_list[turn_of_players - 1] += score
                print(f"{name_of_players_list[turn_of_players - 1]}, your score is: {score_of_players_list[turn_of_players - 1]}")
            else:
                print("The letter is not in the word.")

        if game_running:
            words.pop(random_number)

    for i in range(number_of_players):
        print(f"{name_of_players_list[i]}, your final score is: {score_of_players_list[i]}")

if __name__ == "__main__":
    main()

