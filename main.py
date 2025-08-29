from pipe import pipeline
from plugin import load_plugins


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'
    plugins: dict = load_plugins()

    pipeline(url, plugins=plugins, transform='marxists.org', output='idml')


if __name__ == '__main__':
    main()

"""
    TODO:
    
        MISC
            i.     pull metadata from source -> remove unwanted elements from source -> in that order
            ii.      anchors for detected spelling errors     
            iii.    anchors to indicate more formatting options (future)
            iv.     textacy might be able to improve text processing pipeline instead of custom functions
        
        CLI
            i.      look at the command line arguments API again
            ii.     basic output handling
            iii.    load plugins
    
        PLUGINS
            i.      parameterised plugin loading
            
        OUTPUT
    
            WordPress 
                i.      improve excerpt
                ii.     infobox (plugin)
                
        INPUT
        
            OCR
                i.      look into python libraries for OCR that might be better than my previous attempts
                
        SPELLCHECK
        
            i.  options to disable certain types of checking
            ii. group options into some sort of archetype like 'OCR'
"""
