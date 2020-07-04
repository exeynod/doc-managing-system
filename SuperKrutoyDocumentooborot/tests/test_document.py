import pytest
from documents.document import Document


@pytest.fixture
def setup():
    default_pdf = './SuperKrutoyDocumentooborot/tests/test_docs/default.pdf'
    changed_pdf = './SuperKrutoyDocumentooborot/tests/test_docs/changed.pdf'
    users = [str(i) for i in range(5)]
    return default_pdf, changed_pdf, users


def test_document_init(setup):
    default_pdf, _, users = setup
    d = Document(users[0], default_pdf, True)
    assert d.validate()


def test_sign(setup):
    default_pdf, _, users = setup
    d = Document(users[0], default_pdf, True)
    d.sign()
    assert users[0] in d.who_signed()
    assert len(d.who_signed()) == 1


def test_sign_que(setup):
    default_pdf, _, users = setup
    d = Document(users[0], default_pdf, True)
    for user in users:
        d = Document(user, default_pdf)
        d.sign()
    assert d.who_signed() == users


def test_reset(setup):
    default_pdf, _, users = setup
    d = Document(users[0], default_pdf, True)
    for user in users:
        Document(user, default_pdf).sign()
    assert Document(users[0], default_pdf, True).who_signed() == []
