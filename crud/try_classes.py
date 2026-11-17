class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    def describe(self):
        return f"{self.title} : {self.pages} "


class Ebook(Book):
    def size_mb(self):
        return self.pages * 0.01


book1 = Book("harry", 10)
book2 = Ebook("har", 25)
print(book1.describe())

print(book2.size_mb())
