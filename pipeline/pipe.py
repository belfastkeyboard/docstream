from typing import Any, Callable
import helper
from output import to_docs, to_docx, to_idml, to_txt, to_wordpress
from normalise import normalisation_pipeline
from richtext import RichTextDocument
from input import Metadata, PipelineData, get_pipeline_data

BroadcastFunc = Callable[[RichTextDocument, Metadata], None]
NormaliseFunc = Callable[[RichTextDocument], None]


def get_normalisation() -> list[NormaliseFunc]:
    return normalisation_pipeline()


def get_sender(output: str | list[str] = 'docs') -> list[BroadcastFunc]:
    if isinstance(output, str):
        output = [output]

    senders: dict[str, BroadcastFunc] = {
        'docs': to_docs,
        'docx': to_docx,
        'wordpress': to_wordpress,
        'txt': to_txt,
        'idml': to_idml
    }

    return [senders[o] for o in list(map(lambda o: helper.destination(o), output))]


def run_pipeline(data: PipelineData, normalise: list[NormaliseFunc]) -> None:
    document: RichTextDocument = data['document']

    for func in normalise:
        func(document)


def propagate_data(senders: list[BroadcastFunc], data: PipelineData) -> None:
    for sender in senders:
        sender(data['document'], data['metadata'])


def pipeline(source: Any, plugins: dict, output: str | list[str] = 'docs') -> None:
    senders: list[BroadcastFunc] = get_sender(output)
    normalise: list[NormaliseFunc] = get_normalisation()
    data: PipelineData = get_pipeline_data(source, plugins)

    run_pipeline(data, normalise)
    propagate_data(senders, data)
