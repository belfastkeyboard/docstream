def source(src: str) -> str:
    """

    :param src:
    :return: marxists
    """

    src = src.lower()

    string_map: dict[str, str] = {
        '': '',
        'marxists': 'marxists',
        'marxists.org': 'marxists'
    }

    return string_map[src]


def destination(dest: str) -> str:
    """

    :param dest:
    :return: docs, wordpress, txt, docx, idml
    """

    dest = dest.lower()

    string_map: dict[str, str] = {
        'google': 'docs',
        'docs': 'docs',
        'google-docs': 'docs',
        'googledocs': 'docs',
        'google_docs': 'docs',
        'google docs': 'docs',
        'wp': 'wordpress',
        'word press': 'wordpress',
        'word-press': 'wordpress',
        'word_press': 'wordpress',
        'wordpress': 'wordpress',
        'txt': 'txt',
        'text': 'txt',
        'text file': 'txt',
        'file': 'txt',
        'word': 'docx',
        'docx': 'docx',
        'microsoft word': 'docx',
        'microsoft-word': 'docx',
        'ms word': 'docx',
        'doc': 'docx',
        'idml': 'idml',
        'indesign': 'idml',
        'in design': 'idml',
        'indesign markup': 'idml',
        'indesign mark up': 'idml',
        'indesign file': 'idml',
        'pdf': 'idml'
    }

    return string_map[dest]
