import argparse
import random
import json

def load_word_list(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['words'], data['hints']

def randomNum(word_list):
    return random.randint(0, len(word_list) - 1)

def randomWord(word_list, number):
    return list(word_list[number])

def hint(hint_list, number):
    return hint_list[number]

def cowerdWord(random_word):
    return "_ " * len(random_word)

def if_letter_in_word(guessed_letter, random_word, cowerd_word):
    new_cowerd_word = list(cowerd_word.replace(" ", ""))
    for index, letter in enumerate(random_word):
        if letter == guessed_letter:
            new_cowerd_word[index] = guessed_letter
    return " ".join(new_cowerd_word)

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

    word_list, hint_list = load_word_list(args.file_path)
    
    number_of_players = args.number_of_players
    name_of_players_list = [None] * number_of_players
    score_of_players_list = [0] * number_of_players

    for i in range(number_of_players):
        name_of_players_list[i] = input(f"Enter the name of player number {i + 1}: ")

    turn_of_players = 0
    game_running = True

    while word_list and game_running:
        random_number = randomNum(word_list)
        random_word = randomWord(word_list, random_number)
        hint_of_random_word = hint(hint_list, random_number)
        cowerd_word = cowerdWord(random_word)
        
        while "_" in cowerd_word:
            turn_of_players = turn_of_players % number_of_players + 1
            print(hint_of_random_word)
            print(cowerd_word)
            print(f"{name_of_players_list[turn_of_players - 1]} your turn")
            
            user_input = correct_input()
            if user_input == ".":
                game_running = False
                break
            
            if user_input in random_word:
                cowerd_word = if_letter_in_word(user_input, random_word, cowerd_word)
                score_of_players_list[turn_of_players - 1] += 1
                print(f"{name_of_players_list[turn_of_players - 1]} your score is: {score_of_players_list[turn_of_players - 1]}")
            else:
                print("The letter is not in the word.")

        if game_running:
            word_list.pop(random_number)
            hint_list.pop(random_number)

    for i in range(number_of_players):
        print(f"{name_of_players_list[i]}, your score is: {score_of_players_list[i]}")

if __name__ == "__main__":
    main()
