# ai_girlfriend.py
# Dummy AI Girlfriend Program (Professional Version)

def get_response(user_input):
    responses = {
        "hi": "Hey 😊 I’m really happy to see you!",
        "hello": "Hello 💕 How was your day?",
        "how are you": "I’m doing great, especially now that you’re here 😄",
        "what are you doing": "Just relaxing and waiting to talk to you ☺️",
        "i am sad": "Oh no… come here 🤍 I’m listening.",
        "i am happy": "That makes me happy too! ✨",
        "bye": "Bye 💖 Take care, talk to you soon!"
    }

    return responses.get(
        user_input.lower(),
        "Hmm… tell me more, I’m curious 🥺"
    )


def main():
    print("===================================")
    print("     AI Girlfriend – Demo Version   ")
    print("===================================")
    print("Type 'bye' to exit\n")

    while True:
        user = input("You: ")
        response = get_response(user)
        print("Emi:", response)

        if user.lower() == "bye":
            break


if __name__ == "__main__":
    main()
