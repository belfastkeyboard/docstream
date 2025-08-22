from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org', output='docs')


if __name__ == '__main__':
    main()

"""
    TODO:
        HTML
            i. invert nested quotes
    
        Google Docs
            i. merge nodes before sending, separate nodes with newlines
        
        WordPress 
            i. infobox for wordpress
            ii. author for wordpress (Editorial Team?)
            iii. excerpt for wordpress
            
        inDesign
"""
