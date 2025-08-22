from bs4 import BeautifulSoup
from string import whitespace, punctuation


def marxists_html(soup: BeautifulSoup) -> None:
    to_decompose: list = [
        soup.find('p', class_='toplink'),
        soup.find('p', class_='link'),
        soup.find('p', class_='updat'),
        soup.find('hr', class_='infotop'),
        soup.find('hr', class_='infobot'),
        soup.find("p", class_="updat").find_previous('hr')
    ]

    for element in to_decompose:
        if element:
            element.decompose()


def marxists_title(soup: BeautifulSoup) -> str:
    title: str = ''

    h1 = soup.find('h1')
    if h1:
        title = h1.text

    return title


def marxists_publication(soup: BeautifulSoup) -> str:
    publication: str = ''

    info = soup.select_one('p.info strong')
    if info:
        publication = info.text

    return publication


def marxists_date(soup: BeautifulSoup) -> str:
    date: str = ''

    info = soup.select_one('p.info strong')
    if info:
        date = info.next_sibling.text.strip(whitespace + punctuation)

    return date
