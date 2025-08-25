from pipe import pipeline


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'

    pipeline(url, transform='marxists.org', output='docs')


if __name__ == '__main__':
    main()

"""
    TODO:
        GENERIC TRANSFORM
            i.     invert nested quotes
            ii.    integrate plugins
    
        Google Docs
            i.      build 'runs' out of the document text
        
        WordPress 
            i.      infobox for wordpress
            ii.     author for wordpress (Editorial Team?)
            iii.    excerpt for wordpress
            
        inDesign
"""
