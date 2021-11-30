class Message:
    def __init__(self, author, message, degree=0):
        self.author = author
        self.message = message
        self.degree = degree

    
    def toDict(self) -> dict:
        return {
            "User": self.author.name,
            "Latest Post": self.message.tolist(),
            "Followers": self.degree
        }