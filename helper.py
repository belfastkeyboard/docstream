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
    :return: docs, wordpress, 'txt
    """

    dest = dest.lower()

    string_map: dict[str, str] = {
        'google': 'docs',
        'docs': 'docs',
        'google-docs': 'docs',
        'googledocs': 'docs',
        'google_docs': 'docs',
        'google docs': 'docs',
        'cartlann': 'wordpress',
        'wp': 'wordpress',
        'word press': 'wordpress',
        'word-press': 'wordpress',
        'word_press': 'wordpress',
        'wordpress': 'wordpress',
        'txt': 'txt',
        'text': 'txt',
        'text file': 'txt',
        'file': 'txt',
    }

    return string_map[dest]
