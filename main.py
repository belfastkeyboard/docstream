from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url)


if __name__ == '__main__':
    main()

"""
    TODO: 
        1. pipeline for specific sources i.e. marxists.org
"""
