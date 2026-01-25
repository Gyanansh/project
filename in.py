import random
import json
import os

FILE = "memory.json"

# Load memory
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {"words": {}, "lengths": []}

def learn(text):
    words = text.lower().split()
    memory["lengths"].append(len(words))

    for w in words:
        memory["words"][w] = memory["words"].get(w, 0) + 1

def echo():
    if not memory["words"]:
        return "I don’t know you yet."

    avg_len = sum(memory["lengths"]) // len(memory["lengths"])
    words = list(memory["words"].keys())
    weights = list(memory["words"].values())

    response = random.choices(words, weights=weights, k=avg_len)
    return " ".join(response).capitalize()

def save():
    with open(FILE, "w") as f:
        json.dump(memory, f)

# -------- MAIN LOOP --------
print("🧠 Memory Echo Engine (type 'exit' to stop)\n")

while True:
    user = input("You: ")
    if user.lower() == "exit":
        save()
        print("Echo saved. Goodbye.")
        break

    learn(user)
    print("Echo:", echo())
