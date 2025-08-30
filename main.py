from pipeline import pipeline
from plugin import load_plugins


def main() -> None:
    urls: list[str] = [
        'https://www.marxists.org/archive/connolly/1908/06/harpb.htm',
        'https://www.marxists.org/archive/connolly/1908/07/polact.htm',
        'https://www.marxists.org/archive/connolly/1908/08/davitt.htm',
        'https://www.marxists.org/archive/connolly/1908/09/irmasses.htm',
        'https://www.marxists.org/archive/connolly/1908/09/cathsoc.htm'
    ]

    plugins: dict = load_plugins()

    for url in urls:
        try:
            pipeline(url, plugins=plugins, output='indesign')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()

"""
    TODO:
    
        TEST
            i.      test current setup on docs and wordpress
            ii.     test on one url
            iii.    test on all five urls
    
        MISC
            i.      textacy might be able to improve text processing pipeline instead of custom functions
            ii.     anchors for detected spelling errors     
            iii.    anchors to indicate more formatting options (future)
        
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
                i.      is it possible to convert .idml to .indd ?
                
        INPUT
        
            OCR
                i.      look into python libraries for OCR that might be better than my previous attempts
                
        SPELLCHECK
        
            i.  options to disable certain types of checking
            ii. group options into some sort of archetype like 'OCR'
"""
