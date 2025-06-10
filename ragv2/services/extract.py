from unstructured.partition.auto import partition

def extract_document(filename: str):
    elements = partition(
        filename=filename,
        
        languages=['eng'],
    )

    for el in elements:
        print(el)
    return {}

    texts = []
    tables = []
    s = set()

    for el in elements:
        if el.text:
            texts.append(el.text.strip())

        if el.category == 'Table':
            tables.append(el.text.strip())

    return {
        'text': texts,
        'tables': tables
    }