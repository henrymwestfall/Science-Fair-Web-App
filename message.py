class Message:
    def __init__(self, author, message):
        self.author = author
        self.message = message

        self.viewers = []


    def calculate_feedback(self):
        pass