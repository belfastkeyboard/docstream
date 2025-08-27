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
    
        REBUILD
            i.      google config
            ii.     wordpress config
            iii.    my specific plugins
            iv.     BACK THEM UP
    
        MISC
            i.      anchors for detected spelling errors     
            ii.     anchors to indicate more formatting options (future)
        
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
                
            inDesign
                i.      research API
                
        INPUT
        
            OCR
                i.      look into python libraries for OCR that might be better than my previous attempts
                
        SPELLCHECK
"""
