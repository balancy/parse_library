import argparse

import requests

from book import Book

BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
SITE_URL = "https://tululu.org/"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download books (title, author, genre, image, comments).")
    parser.add_argument("start_id", help="Book id to start parsing with")
    parser.add_argument("end_id", help="Book id to end parsing with")
    args = parser.parse_args()

    requests.packages.urllib3.disable_warnings()

    Book.check_folders(books_folder=BOOKS_FOLDER, images_folder=IMAGES_FOLDER)

    for book_id in range(int(args.start_id), int(args.end_id)):
        try:
            book = Book(book_id=book_id)
            html = book.get_html()

            # title, author
            title, author = book.get_title_image(html)
            print(f"Название: {title}")
            print(f"Автор: {author}")

            # image
            relative_image_url = book.get_image_url(html)
            path_image_on_disc = book.download_image(relative_image_url)

            # text
            relative_txt_url = book.get_txt_link(html)
            if not relative_txt_url:
                path_txt_on_disc = book.download_txt(relative_txt_url, title)

            # comments
            comments = book.get_comments(html)

            # genre
            genre = book.get_genre(html)

            print()

        except requests.HTTPError:
            pass
