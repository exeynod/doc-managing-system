from django.test import TestCase
from documents.document import Document


test_file_1 = 'SuperKrutoyDocumentooborot/test_1.pdf'
test_file_2 = 'SuperKrutoyDocumentooborot/test_2.pdf'
users = [str(i) for i in range(5)]


class DefaultTestCase(TestCase):

    def test_for_test(self):
        self.assertTrue(True)

    '''def test_document_init(self):
        d = Document(users[0], test_file_1, True)
        self.assertTrue(d.validate())

    def test_sign(self):
        d = Document(users[0], test_file_1, True)
        d.sign()
        self.assertTrue(users[0] in d.who_signed())
        self.assertEqual(len(d.who_signed()), 1)

    def test_wrong_file(self):
        d = Document(users[0], test_file_1, True)
        d.path = test_file_2'''