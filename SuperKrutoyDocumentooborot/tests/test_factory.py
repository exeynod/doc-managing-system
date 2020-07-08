import pytest
from documents.document import Document
from documents.factory_document import Creator


@pytest.mark.parametrize('path', ('', '21837213', '.pdf'))
def test_right_creation(path):
    path = f'./SuperKrutoyDocumentooborot/tests/test_docs/right/{path}'
    assert isinstance(Creator.create(path + '.pdf', '1', True), Document)
    assert isinstance(Creator.create(path + '.docx', '1', True), Document)


@pytest.mark.parametrize('path', ('.doc', '.pdf21837213', '.pdf.doc'))
def test_unsuitable_extension(path):
    with pytest.raises(ValueError) as exinfo:
        Creator.create(path, '1', True)
    assert 'Invalid extension' in str(exinfo.value)
