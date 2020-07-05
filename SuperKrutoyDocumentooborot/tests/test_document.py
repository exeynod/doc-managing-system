import pytest
from documents.pdf_document import PDFDocument
from documents.docx_document import DOCXDocument


@pytest.fixture
def setup():
    default_path = './SuperKrutoyDocumentooborot/tests/test_docs/default'
    users = [str(i) for i in range(5)]
    return default_path, users


@pytest.mark.parametrize('cls, file', [(PDFDocument, '.pdf'), (DOCXDocument, '.docx')])
def test_document_init(cls, file, setup):
    default_path, users = setup
    file = default_path + file
    d = cls(users[0], file, True)
    assert d.validate()


@pytest.mark.parametrize('cls, file', [(PDFDocument, '.pdf'), (DOCXDocument, '.docx')])
def test_sign(cls, file, setup):
    default_path, users = setup
    file = default_path + file
    d = cls(users[0], file, True)
    d.sign()
    assert users[0] in d.who_signed()
    assert len(d.who_signed()) == 1


@pytest.mark.parametrize('cls, file', [(PDFDocument, '.pdf'), (DOCXDocument, '.docx')])
def test_sign_que(cls, file, setup):
    default_path, users = setup
    file = default_path + file
    d = cls(users[0], file, True)
    for user in users:
        d = cls(user, file)
        d.sign()
    assert d.who_signed() == users


@pytest.mark.parametrize('cls, file', [(PDFDocument, '.pdf'), (DOCXDocument, '.docx')])
def test_reset(cls, file, setup):
    default_path, users = setup
    file = default_path + file
    cls(users[0], file, True)
    for user in users:
        cls(user, file).sign()
    assert cls(users[0], file, True).who_signed() == []
