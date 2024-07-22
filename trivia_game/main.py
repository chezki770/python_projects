import random
import json
import argparse
import requests
from pydantic import BaseModel, ValidationError
from collections import Counter

class QuestionModel(BaseModel):
    question: str
    options: list
    correct_answer: int
    category: str
    difficulty: str

class Question:
    def __init__(self, question, options, correct_answer, category, difficulty):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.category = category
        self.difficulty = difficulty

    def is_correct(self, answer):
        return self.correct_answer == answer

def load_questions(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return parse_questions(data)

def fetch_questions(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return parse_questions(data)
    except requests.RequestException as e:
        print(f"Error fetching questions: {e}")
        return []

def parse_questions(data):
    questions = []
    for q in data:
        try:
            question = QuestionModel(**q)
            questions.append(Question(
                question.question,
                question.options,
                question.correct_answer,
                question.category,
                question.difficulty
            ))
        except ValidationError as e:
            print(f"Error in question format: {e}")
    return questions

class TriviaGame:
    def __init__(self, questions):
        self.questions = questions
        self.current_question = None
        self.scores = [0, 0]
        self.current_player = 0

    def select_question(self, category=None, difficulty=None):
        available_questions = [q for q in self.questions if (category is None or q.category.lower() == category.lower()) and (difficulty is None or q.difficulty.lower() == difficulty.lower())]
        if not available_questions:
            print("No questions available for the selected category and difficulty.")
            return False
        self.current_question = random.choice(available_questions)
        return True

    def ask_question(self):
        print(f"\nPlayer {self.current_player + 1}'s turn:")
        print(f"Question: {self.current_question.question}")
        options = list(enumerate(self.current_question.options, 1))
        random.shuffle(options)
        for idx, option in options:
            print(f"{idx}. {option}")

    def check_answer(self, answer):
        if self.current_question.is_correct(answer):
            print("Correct!")
            self.scores[self.current_player] += 1
            return True
        else:
            print("Wrong answer.")
            return False

    def next_turn(self):
        self.current_player = (self.current_player + 1) % 2

    def play(self):
        while self.questions:
            category = input("\nChoose a category (Geography, Math, Literature, Science, History, Art, Music, or press Enter for any): ")
            difficulty = input("Choose a difficulty (easy, medium, hard, or press Enter for any): ")
            if not self.select_question(category or None, difficulty or None):
                continue
            self.ask_question()
            while True:
                try:
                    answer = int(input("Your answer (1-4): ")) - 1
                    if 0 <= answer < len(self.current_question.options):
                        break
                    else:
                        print("Invalid input. Please enter a number between 1 and 4.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            if self.check_answer(answer):
                self.questions.remove(self.current_question)
            self.next_turn()
            self.print_scores()
        self.print_final_scores()

    def print_scores(self):
        print(f"\nCurrent scores: Player 1: {self.scores[0]}, Player 2: {self.scores[1]}")

    def print_final_scores(self):
        print("\nGame Over!")
        print(f"Final scores: Player 1: {self.scores[0]}, Player 2: {self.scores[1]}")
        if self.scores[0] > self.scores[1]:
            print("Player 1 wins!")
        elif self.scores[1] > self.scores[0]:
            print("Player 2 wins!")
        else:
            print("It's a tie!")

def get_categories(questions):
    return sorted(set(q.category for q in questions))

def get_difficulties(questions):
    return sorted(set(q.difficulty for q in questions))

def display_stats(questions):
    categories = get_categories(questions)
    difficulties = get_difficulties(questions)
    category_counts = Counter(q.category for q in questions)
    difficulty_counts = Counter(q.difficulty for q in questions)

    print("\nAvailable Categories:")
    for category in categories:
        print(f"- {category} ({category_counts[category]} questions)")

    print("\nAvailable Difficulties:")
    for difficulty in difficulties:
        print(f"- {difficulty} ({difficulty_counts[difficulty]} questions)")

    print(f"\nTotal number of questions: {len(questions)}\n")

def main():
    parser = argparse.ArgumentParser(description="Trivia Game")
    parser.add_argument("--file", help="Path to the JSON file with questions")
    parser.add_argument("--api", help="URL of the API to fetch questions")
    args = parser.parse_args()

    if args.file:
        questions = load_questions(args.file)
    elif args.api:
        questions = fetch_questions(args.api)
    else:
        print("Please provide either a file path or an API URL.")
        return

    if not questions:
        print("No questions loaded. Exiting.")
        return

    display_stats(questions)

    play_game = input("Do you want to start the game? (yes/no): ").lower().strip()
    if play_game == 'yes':
        game = TriviaGame(questions)
        game.play()
    else:
        print("Game cancelled. Goodbye!")

if __name__ == "__main__":
    main()
    
    
