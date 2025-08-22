from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org', output='wordpress')


if __name__ == '__main__':
    main()

"""
    TODO:
        1. WordPress 
            i. invert quotes for wordpress
            ii. infobox for wordpress
            iii. author for wordpress (Editorial Team?)
            iv. excerpt for wordpress
            
        2. inDesign also has a programmatic API for generating documents
"""
