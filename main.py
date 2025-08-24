from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org', output='docs')


if __name__ == '__main__':
    main()

"""
    TODO:
        PLUGIN ARCHITECTURE
            i. create basic architecture
            
        GENERIC TRANSFORM
            i. actually do this
            ii. integrate plugins
    
        HTML
            i. invert nested quotes
    
        Google Docs
            i. docs output formatting is broken
            ii. seems to be the result of a normalisation function that strips all newlines 
        
        WordPress 
            i. infobox for wordpress
            ii. author for wordpress (Editorial Team?)
            iii. excerpt for wordpress
            
        inDesign
"""
