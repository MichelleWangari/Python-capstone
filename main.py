from pymongo import MongoClient
import matplotlib.pyplot as plt

# MongoDB connection
client = MongoClient("mongodb+srv://michellewangari33:FQruLtRVeH7iRI6X@cluster0.ligucf1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client["polling"]
polls = db["polls"]
votes = db["votes"]
user_votes = db["user_votes"]

# Poll topics
CATEGORIES = {
    "meal_type": {
        "question": "Which type of meal do you prefer?",
        "options": ["Breakfast", "Lunch", "Dinner", "Tea"]
    },
    "favorite_food": {
        "question": "What's your favorite food?",
        "options": ["Pizza", "Ugali", "Rice", "Chips"]
    },
    "favorite_drink": {
        "question": "What's your favorite drink?",
        "options": ["Water", "Juice", "Soda", "Tea"]
    }
}

# Initialize DB with polls and vote counts
def setup_polls():
    for cat, data in CATEGORIES.items():
        if polls.count_documents({"category": cat}) == 0:
            polls.insert_one({
                "category": cat,
                "question": data["question"],
                "options": data["options"]
            })
            for opt in data["options"]:
                votes.insert_one({
                    "category": cat,
                    "option": opt,
                    "count": 0
                })

# Show poll categories
def select_category():
    print("Select Poll Category:")
    for idx, cat in enumerate(CATEGORIES.keys(), start=1):
        print(f"{idx}. {cat.replace('_', ' ').title()}")
    try:
        choice = int(input("Enter your choice: "))
        cat = list(CATEGORIES.keys())[choice - 1]
        return cat
    except:
        print("Invalid input.")
        return None

# Voting process
def vote():
    username = input(" Enter your name: ").strip().lower()
    if not username:
        print("Username cannot be empty.")
        return

    cat = select_category()
    if not cat:
        return

    poll = polls.find_one({"category": cat})
    print(f"{poll['question']}")
    for idx, opt in enumerate(poll['options'], start=1):
        print(f"{idx}. {opt}")

    try:
        choice = int(input("Your vote: "))
        selected = poll['options'][choice - 1]
        votes.update_one(
            {"category": cat, "option": selected},
            {"$inc": {"count": 1}}
        )
        user_votes.insert_one({
            "username": username,
            "category": cat,
            "option": selected
        })
        print(f"Vote by '{username}' recorded.")
    except:
        print("Invalid input.")

# Display text results and chart
def show_results():
    cat = select_category()
    if not cat:
        return
    poll = polls.find_one({"category": cat})
    vote_data = list(votes.find({"category": cat}))
    total = sum(v["count"] for v in vote_data)

    print(f"Results for: {poll['question']}")
    for v in vote_data:
        percent = (v["count"] / total * 100) if total else 0
        bar = "█" * int(percent // 2)
        print(f"{v['option']:<20} [{bar:<50}] {v['count']} votes ({percent:.1f}%)")

    print(f"\nTotal votes: {total}")
    plot_bar_chart(vote_data, poll["question"])

# Create bar chart using matplotlib
def plot_bar_chart(vote_data, question):
    labels = [v["option"] for v in vote_data]
    counts = [v["count"] for v in vote_data]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, counts, color="skyblue", edgecolor="black")

    plt.title(question)
    plt.xlabel("Options")
    plt.ylabel("Number of Votes")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), ha="center", va="bottom")

    plt.tight_layout()
    plt.show()

# Menu
def menu():
    print("--- Multi-Poll Voting App ---")
    print("1. Vote in a Poll")
    print("2. View Results")
    print("3. Exit")
    return input("Select an option: ")

# Run
if __name__ == "__main__":
    setup_polls()
    while True:
        choice = menu()
        if choice == "1":
            vote()
        elif choice == "2":
            show_results()
        elif choice == "3":
            print("Bye!")
            break
        else:
            print("Invalid choice.")
