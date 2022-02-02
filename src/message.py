class Message:
    def __init__(self, author, message, views=0):
        self.author = author
        self.message = message
        self.viewers = []


    @property
    def views(self) -> int:
        return len(self.viewers)

    
    def to_dict(self) -> dict:
        return {
            "User": self.author.name,
            "Latest Post": self.message.tolist(),
            "Views": self.views
        }