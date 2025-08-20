from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org')


if __name__ == '__main__':
    main()

"""
    TODO: 
        1. after text styles have been calculated, all the text can be sent in one request (theoretically)
        2. wordpress has a REST API that can create pages
        3. inDesign also has a programmatic API for generating documents
"""
