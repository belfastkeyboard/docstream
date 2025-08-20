from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org', output='wordpress')


if __name__ == '__main__':
    main()

"""
    TODO: 
        1. wordpress has a REST API that can create pages
        2. inDesign also has a programmatic API for generating documents
"""
