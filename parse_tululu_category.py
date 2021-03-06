from bs4 import BeautifulSoup
import requests

URL_SITE = "https://tululu.org"
URL_SYFY_SUFFIX = "/l55/"


def check_for_redirect(status_code) -> None:
    """Checks if given status_code is redirect status code.
    :param status_code: given status_code
    """

    if status_code == 302:
        raise requests.HTTPError


def find_books_urls(start_page, end_page):
    """Find sy-fy books urls from pages
    starting from start_page and finishing at end_page.

    :param start_page: page to start looking books from
    :param end_page: page to finish looking books at
    :return: books urls
    """

    if start_page < 1:
        print("Задайте стартовую страницу больше или равную 1")
        return

    if start_page > end_page:
        print("Стартовая страница не может быть больше конечной страницы.")
        return

    all_books = []
    for pagenumber in range(start_page, end_page+1):
        response = requests.get(
            f"{URL_SITE}{URL_SYFY_SUFFIX}{pagenumber}",
            verify=False, allow_redirects=False
        )
        response.raise_for_status()
        check_for_redirect(response.status_code)

        soup = BeautifulSoup(response.content, "lxml")

        selector = "#content [title*='читать online']"
        for book in soup.select(selector):
            all_books.append(f"{URL_SITE}{book['href']}")

    return all_books


def find_last_page_number() -> int:
    """Finds last page number in sci-fi category.

    :return: last page number
    """

    response = requests.get(
        f"{URL_SITE}{URL_SYFY_SUFFIX}",
        verify=False, allow_redirects=False
    )
    response.raise_for_status()
    check_for_redirect(response.status_code)

    soup = BeautifulSoup(response.content, "lxml")

    return int(soup.select("a.npage")[-1].text)
