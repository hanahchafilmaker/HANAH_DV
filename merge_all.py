from docx import Document

def merge_docs(files, output):
    merged = Document()

    for i, file in enumerate(files):
        sub = Document(file)

        if i != 0:
            merged.add_page_break()

        for el in sub.element.body:
            merged.element.body.append(el)

    merged.save(output)