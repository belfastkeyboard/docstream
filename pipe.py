from typing import Callable
import helper
from output import to_docs, to_docx, to_idml, to_txt, to_wordpress
from normalise import normalisation_pipeline
from richtext import RichTextDocument
from input import PipelineData, get_pipeline_data


def _get_normalisation(**kwargs) -> list[Callable[[RichTextDocument], None]]:
    return normalisation_pipeline(**kwargs)


def _get_sender(output: str = 'docs', **kwargs) -> Callable[[...], None]:
    senders: dict[str, Callable[[...], None]] = {
        'docs': to_docs,
        'docx': to_docx,
        'wordpress': to_wordpress,
        'txt': to_txt,
        'idml': to_idml
    }

    output = helper.destination(output)

    return senders[output]


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
