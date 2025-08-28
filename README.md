# Plugins

1. Modify source

JSON example:
```
{
    "modify-source": {
        "filename": ["function_name", "another_function"]
    },
    "adaptor": {
        "filename": ["function_name", "another_function"]
    },
}
```

### modify-source 

`def name(content: Any, **kwargs) -> Any:`

### adaptor

`def name(document: RichTextDocument) -> None:`