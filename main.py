import requests

from book import Book

BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
SITE_URL = "https://tululu.org/"
NUMBER_BOOKS = 10

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()

    Book.check_folders(books_folder=BOOKS_FOLDER, images_folder=IMAGES_FOLDER)

    for book_id in range(1, NUMBER_BOOKS):
        try:
            print(book_id)
            book = Book(book_id=book_id)
            html = book.get_html()

            title, relative_image_url = book.get_title_image(html)
            path_image_on_disc = book.download_image(relative_image_url)

            relative_txt_url = book.get_txt_link(html)
            if not relative_txt_url:
                path_txt_on_disc = book.download_txt(relative_txt_url, title)

            comments = book.get_comments(html)
            genre = book.get_genre(html)

        except requests.HTTPError:
            print(f"There is no article for book with id={book_id}")
