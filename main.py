from pipe import pipeline
from plugin import load_plugins


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'
    plugins: dict = load_plugins()

    pipeline(url, plugins=plugins, transform='marxists.org', output='docx')


if __name__ == '__main__':
    main()

"""
    TODO:
        MISC
            i.      replace marxists in transform.py with plugins
    
        GENERIC TRANSFORM
            i.      invert nested quotes
    
        PLUGINS
            i.      parameterised plugin loading
            
            
        OUTPUT
    
            WordPress 
                i.      improve excerpt
                ii.     infobox
                
            inDesign
            
            .docx
                i.      install lib
                ii.     open document
                iii.    dump to doc
                iv.     create doc run (share with google docs?)
                v.      formatted doc file
"""
