from typing import Callable
import helper
from output import to_docs, to_docx, to_txt, to_wordpress
from normalise import normalisation_pipeline
from richtext import RichTextDocument
from input import PipelineData, get_pipeline_data


def _get_normalisation(**kwargs) -> list[Callable[[RichTextDocument], None]]:
    return normalisation_pipeline(**kwargs)


def _get_sender(output: str = 'docs', **kwargs) -> Callable[[...], None]:
    output = helper.destination(output)

    if output == 'docs':
        return to_docs
    elif output == 'docx':
        return to_docx
    elif output == 'wordpress':
        return to_wordpress
    elif output == 'txt':
        return to_txt

    raise ValueError(f'{output} not recognised')


def _run_pipeline(data: PipelineData, normalise: list[Callable[[RichTextDocument], None]]) -> None:
    document: RichTextDocument = data['document']

    for func in normalise:
        func(document)


def pipeline(source, **kwargs) -> None:
    """
    WIP

    Simple way to chain together all the operations required to send to the output

    :param source: url
    :return: None
    """

    sender: Callable[[...], None] = _get_sender(**kwargs)
    normalise: list[Callable[[RichTextDocument], None]] = _get_normalisation(**kwargs)
    data: PipelineData = get_pipeline_data(source, **kwargs)

    _run_pipeline(data, normalise)

    sender(**data)
