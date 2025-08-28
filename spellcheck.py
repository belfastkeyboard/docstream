from language_tool_python import LanguageTool
from richtext import RichText, RichTextDocument
from anchors import remove_anchors


def setup_spellchecker() -> LanguageTool:
    spellchecker = LanguageTool('en-GB')

    # spellchecker.disabled_categories = {'STYLE', 'MISC', 'TYPOGRAPHY'}
    # spellchecker.disabled_rules = {
    #     'IN_THE_MOMENT', 'OXFORD_SPELLING_Z_NOT_S', 'MORFOLOGIK_RULE_EN_GB', 'ALL_OF_THE', 'EVEN_ALTHOUGH'
    # }

    return spellchecker


def print_mistake(mistake) -> None:
    separator: str = '-' * len(mistake.context)
    context: str = remove_anchors(mistake.context)
    mistake_pos: int = mistake.offsetInContext
    mistake_len: int = mistake.errorLength
    point_out_error: str = f'{" " * mistake_pos}{"^" * mistake_len}'
    message: str = f'Reason: {mistake.message}'
    suggestions = mistake.replacements
    suggestion_count: int = len(suggestions)
    suggestion_prefix: str = f'Suggestion{"s" if suggestion_count > 1 else ""}: '

    print(separator)
    print(context)
    print(point_out_error)
    print(message)

    if suggestions:
        print(suggestion_prefix, end='')

        for i, suggestion in enumerate(suggestions):
            suggestion: str = f'{i + 1}. "{suggestion}"'
            end: str = ', ' if i < suggestion_count - 1 else '\n'
            print(suggestion, end=end)
    else:
        print('Press 1 to fix.')

    print(separator, end='\n')


def fix_mistake(mistake, rt: RichText) -> None:
    get: str = input('> ')

    try:
        index: int = int(get) - 1
        fix: str = mistake.replacements[index]
    except (IndexError, ValueError):
        return

    cut1: int = mistake.offset
    cut2: int = cut1 + mistake.errorLength

    rt.text = rt.text[:cut1] + fix + rt.text[cut2:]


def spellcheck_rich_text(rt: RichText, spellchecker: LanguageTool) -> None:
    mistakes = spellchecker.check(rt.text)

    for mistake in mistakes:
        print_mistake(mistake)
        fix_mistake(mistake, rt)


def spellcheck_document(document: RichTextDocument) -> None:
    spellchecker: LanguageTool = setup_spellchecker()

    for rt in document.texts:
        spellcheck_rich_text(rt, spellchecker)
