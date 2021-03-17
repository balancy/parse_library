import requests

from book import Book

BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
SITE_URL = "https://tululu.org/"
NUMBER_BOOKS = 10

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()

    for book_id in range(1, NUMBER_BOOKS):
        try:
            book = Book(books_folder=BOOKS_FOLDER, image_folder=IMAGES_FOLDER, site_url=SITE_URL, book_id=book_id)
            book.create_dirs()
            html = book.get_html()

            title, image_url = book.get_title_image(html)
            path_image_on_disc = book.download_image(image_url)

            relative_txt_url = book.get_txt_link(html)
            path_txt_on_disc = book.download_txt(relative_txt_url, title)

            comments = book.get_comments(html)
        except requests.HTTPError:
            print(f"For book with id={book_id} there is a redirection")
        except FileNotFoundError:
            print(f"For book with id={book_id} txt file is not found")
