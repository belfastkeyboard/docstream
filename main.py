from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org')


if __name__ == '__main__':
    main()

"""
    TODO: 
        1. pipeline transform can apply specific styles
        2. after text styles have been calculated, all the text can be sent in one request (theoretically)
"""
