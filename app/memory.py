class ConversationMemory:
    def __init__(self):
        self.history = []

    def add_interaction(self, question, answer):
        self.history.append({"question": question, "answer": answer})

    def get_history(self):
        return self.history

    def clear(self):
        self.history = []