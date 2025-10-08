import requests
import google.generativeai as genai

# === CONFIGURATION ===
USE_PROVIDER = "openrouter"  # Options: "gemini" or "openrouter"

# Gemini API Keya
GEMINI_API_KEY = "your_gemini_api_key"

# OpenRouter API Key and Model
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "alibaba/tongyi-deepresearch-30b-a3b:free"

# === SETUP ===
if USE_PROVIDER == "gemini":
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-pro")

def get_ai_word(difficulty):
    if difficulty == "easy":
        prompt = "Choose a random common English word with 4 to 5 letters. Just return the word, no explanation."
    elif difficulty == "medium":
        prompt = "Choose a random English word with 6 to 8 letters. Just return the word, no explanation."
    elif difficulty == "hard":
        prompt = "Choose a random uncommon or tricky English word with more than 8 letters. Just return the word, no explanation."
    else:
        raise ValueError("Invalid difficulty level")

    if USE_PROVIDER == "gemini":
        response = gemini_model.generate_content(prompt)
        word = response.text.strip().lower()
    elif USE_PROVIDER == "openrouter":
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        # Be defensive: ensure the API returned the expected structure
        try:
            response_json = response.json()
        except ValueError:
            print("❌ Error: OpenRouter returned non-JSON response")
            print(response.text)
            raise ValueError("Failed to get word from OpenRouter: non-JSON response")

        if "choices" in response_json and response_json["choices"]:
            # Guard against missing nested keys
            message = response_json["choices"][0].get("message", {})
            content = message.get("content", "").strip()
            word = content.lower()
        else:
            print("❌ Error from OpenRouter API:")
            print(response_json)
            raise ValueError("Failed to get word from OpenRouter. Check your API key or model.")
    else:
        raise ValueError("Unsupported provider")

    return ''.join(filter(str.isalpha, word))  # Clean up any extra characters

def draw_hangman(attempts_left):
    stages = [
        """
  +---+
|   |
      |
      |
      |
      |
========""",
        """
  +---+
|   |
  O   |
      |
      |
      |
========""",
        """
  +---+
|   |
  O   |
|   |
      |
      |
========""",
        """
  +---+
|   |
  O   |
 /|   |
      |
      |
========""",
        """
  +---+
|   |
  O   |
 /|\\  |
      |
      |
========""",
        """
  +---+
|   |
  O   |
 /|\\  |
 /    |
      |
========""",
        """
  +---+
|   |
  O   |
 /|\\  |
 / \\  |
      |
========"""
    ]
    print(stages[6 - attempts_left])

def play_hangman(word):
    guessed = set()
    attempts = 6
    display = ['_' for _ in word]

    print("\n🎮 New Round: Guess the word chosen by AI.")

    while attempts > 0 and '_' in display:
        print("\nWord:", ' '.join(display))
        print("Guessed letters:", ', '.join(sorted(guessed)))
        print(f"Remaining attempts: {attempts}")
        draw_hangman(attempts)
        guess = input("Enter a letter: ").lower()

        if not guess.isalpha() or len(guess) != 1:
            print("Please enter a single alphabet.")
            continue

        if guess in guessed:
            print("You already guessed that letter.")
            continue

        guessed.add(guess)

        if guess in word:
            for i, letter in enumerate(word):
                if letter == guess:
                    display[i] = guess
            print("✅ Correct!")
        else:
            attempts -= 1
            print("❌ Wrong!")

    if '_' not in display:
        print(f"\n🎉 You won! The word was '{word}'.")
        return True
    else:
        draw_hangman(0)
        print(f"\n💀 Game over! The word was '{word}'.")
        return False

def main():
    print("🎮 Welcome to AI Hangman!")
    print("Select difficulty level: easy / medium / hard")
    difficulty = input("Enter difficulty: ").strip().lower()

    score = 0
    round_number = 1

    while True:
        print(f"\n🔁 Round {round_number}")
        try:
            word = get_ai_word(difficulty)
            won = play_hangman(word)
            if won:
                score += 10
            else:
                score -= 5
            print(f"🏆 Current Score: {score}")
        except ValueError as e:
            print(e)
            break

        again = input("\nDo you want to play another round? (yes/no): ").strip().lower()
        if again != "yes":
            break
        round_number += 1

    print(f"\n🎯 Final Score: {score}")
    print("Thanks for playing!")

if __name__ == "__main__":
    main()
