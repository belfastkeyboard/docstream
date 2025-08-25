from pipe import pipeline
from plugin import load_plugins


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'
    plugins: dict = load_plugins()

    pipeline(url, plugins=plugins, transform='marxists.org', output='wordpress')


if __name__ == '__main__':
    main()

"""
    TODO:
        MISC
            i.      replace marxists in transform.py with plugins
    
        GENERIC TRANSFORM
            i.     invert nested quotes
            ii.    integrate plugins
    
        PLUGINS
            i.      parameterised plugin loading
    
        Google Docs
            i.      build 'runs' out of the document text
        
        WordPress 
            i.      infobox for wordpress
            ii.     author for wordpress (Editorial Team?)
            iii.    excerpt for wordpress
            
        inDesign
"""
