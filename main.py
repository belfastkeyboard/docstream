from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org')


if __name__ == '__main__':
    main()

"""
    TODO: 
        1. pipeline transform can apply specific styles
"""
