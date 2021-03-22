import argparse
import os

from scripts_extract_bookpage_elements import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download books (title, author, genre, image, comments).")
    parser.add_argument("start_id", help="Book id to start parsing with", type=int)
    parser.add_argument("end_id", help="Book id to end parsing with", type=int)
    args = parser.parse_args()

    requests.packages.urllib3.disable_warnings()

    os.makedirs(BOOKS_FOLDER, exist_ok=True)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)

    for book_id in range(args.start_id, args.end_id):
        try:
            soup = fetch_parsed_html(book_id)
        except requests.HTTPError:
            continue

        # title, author
        title, author = extract_title_author(soup)
        print(f"Название: {title}\nАвтор: {author}")

        # image
        image_url = extract_image_url(soup)
        path_image = download_image_return_path(image_url)
        print(f"Путь к изображению: '{path_image}'")

        # text
        txt_url = extract_txt_url(soup)
        if txt_url:
            path_txt = download_txt_return_path(txt_url, title)
            print(f"Путь к текстовой версии книги: '{path_txt}'")

        # comments
        comments = extract_comments(soup)
        if comments:
            print(f"Комментарии: {'; '.join(comments)}")

        # genre
        genre = extract_genre(soup)
        print(f"Жанр книги: {', '.join(genre)}")

        print()
