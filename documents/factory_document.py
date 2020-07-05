from __future__ import annotations
from documents.document import Document
from documents.pdf_document import PDFDocument


class Creator:

    @staticmethod
    def create(path_to_file, user_id, primary=False) -> Document:
        if path_to_file[len(path_to_file) - 4:] == '.pdf':
            return PDFDocument(user_id, path_to_file, primary)
        raise ValueError('Invalid extension')
