# Plugins

JSON example:
```
{
    "modify-source": {
        "filename": ["function", "another_function"]
    },
    "adaptor": {
        "filename": ["function", "another_function"]
    },
    "metadata": {
        "filename": ["function", "another_function"]
    }
}
```

### modify-source 

`def name(content: Any, **kwargs) -> Any:`

### adaptor

`def name(document: RichTextDocument) -> None:`

### metadata

`def name(ent: Any, meta: dict[str, str]) -> None:`