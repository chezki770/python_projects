import random
import json
import argparse
import requests
from pydantic import BaseModel, ValidationError
from collections import Counter
from typing import List, Optional

class QuestionModel(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    category: str
    difficulty: str

class Question:
    def __init__(self, question: str, options: List[str], correct_answer: int, category: str, difficulty: str):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.category = category
        self.difficulty = difficulty

    def is_correct(self, answer: int) -> bool:
        return self.correct_answer == answer

def load_questions(file_path: str) -> List[Question]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return parse_questions(data)

def fetch_questions(api_url: str) -> List[Question]:
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return parse_questions(data)
    except requests.RequestException as e:
        print(f"Error fetching questions: {e}")
        return []

def parse_questions(data: List[dict]) -> List[Question]:
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
    def __init__(self, questions: List[Question], num_players: int):
        self.questions = questions
        self.current_question: Optional[Question] = None
        self.scores = [0] * num_players
        self.current_player = 0
        self.num_players = num_players
        self.player_names = self.get_player_names()

    def get_player_names(self) -> List[str]:
        """Prompt for player names."""
        player_names = []
        for i in range(self.num_players):
            while True:
                name = input(f"Enter the name for Player {i + 1}: ").strip()
                if name:
                    player_names.append(name)
                    break
                print("Player name cannot be empty. Please enter a valid name.")
        return player_names

    def select_question(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> bool:
        """Select a question based on category and difficulty."""
        available_questions = [
            q for q in self.questions if 
            (category is None or q.category.lower() == category.lower()) and 
            (difficulty is None or q.difficulty.lower() == difficulty.lower())
        ]
        if not available_questions:
            print("No questions available for the selected category and difficulty.")
            return False
        self.current_question = random.choice(available_questions)
        return True

    def ask_question(self):
        """Ask the current question to the current player."""
        print(f"\n{self.player_names[self.current_player]}'s turn:")
        print(f"Question: {self.current_question.question}")
        for idx, option in enumerate(self.current_question.options, 1):
            print(f"{idx}. {option}")

    def get_answer(self) -> int:
        """Get the player's answer with validation."""
        while True:
            try:
                answer = int(input("Your answer (1-4): ")) - 1
                if 0 <= answer < len(self.current_question.options):
                    return answer
                else:
                    print("Invalid input. Please enter a number between 1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def check_answer(self, answer: int) -> bool:
        """Check if the given answer is correct."""
        if self.current_question.is_correct(answer):
            print("Correct!")
            self.scores[self.current_player] += 1
            return True
        else:
            print("Wrong answer.")
            return False

    def next_turn(self):
        """Move to the next player's turn."""
        self.current_player = (self.current_player + 1) % self.num_players

    def play(self):
        """Start the trivia game."""
        while self.questions:
            category = input("\nChoose a category (Geography, Math, Literature, Science, History, Art, Music, or press Enter for any): ").strip()
            difficulty = input("Choose a difficulty (easy, medium, hard, or press Enter for any): ").strip()
            if not self.select_question(category or None, difficulty or None):
                continue
            self.ask_question()
            answer = self.get_answer()
            if self.check_answer(answer):
                self.questions.remove(self.current_question)
            self.next_turn()
            self.print_scores()
        self.print_final_scores()

    def print_scores(self):
        """Print the current scores of all players."""
        print("\nCurrent scores:")
        for name, score in zip(self.player_names, self.scores):
            print(f"{name}: {score}")

    def print_final_scores(self):
        """Print the final scores and announce the winner."""
        print("\nGame Over!")
        for name, score in zip(self.player_names, self.scores):
            print(f"{name}: {score}")
        max_score = max(self.scores)
        winners = [name for name, score in zip(self.player_names, self.scores) if score == max_score]
        if len(winners) == 1:
            print(f"{winners[0]} wins!")
        else:
            print(f"It's a tie between: {', '.join(winners)}")

def get_categories(questions: List[Question]) -> List[str]:
    """Get a sorted list of unique categories."""
    return sorted(set(q.category for q in questions))

def get_difficulties(questions: List[Question]) -> List[str]:
    """Get a sorted list of unique difficulties."""
    return sorted(set(q.difficulty for q in questions))

def display_stats(questions: List[Question]):
    """Display statistics about the available questions."""
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
        while True:
            try:
                num_players = int(input("Enter the number of players: "))
                if num_players > 0:
                    break
                else:
                    print("Number of players must be greater than 0.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        game = TriviaGame(questions, num_players)
        game.play()
    else:
        print("Game cancelled. Goodbye!")

if __name__ == "__main__":
    main()

