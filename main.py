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
        TRANSFORM
            i.      split RichText on newlines
    
        PLUGINS
            i.      parameterised plugin loading
            
        OUTPUT
    
            WordPress 
                i.      improve excerpt
                ii.     infobox (plugin)
                
            inDesign
                i.      research API
"""
