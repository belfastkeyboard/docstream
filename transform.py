from bs4 import BeautifulSoup


def marxists_html(soup: BeautifulSoup) -> None:
    to_decompose: list = [
        soup.find('p', class_='toplink'),
        soup.find('p', class_='link'),
        soup.find('p', class_='updat'),
        soup.find('hr', class_='infotop'),
        soup.find('hr', class_='infobot')
    ]

    for element in to_decompose:
        if element:
            element.decompose()
