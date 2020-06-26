from django.test import TestCase
from documents.document import Document


test_file_1 = 'SuperKrutoyDocumentooborot/1_test.pdf'
test_file_2 = 'SuperKrutoyDocumentooborot/test.pdf'
users = [str(i) for i in range(5)]


class DefaultTestCase(TestCase):

    def test_for_test(self):
        self.assertTrue(True)

    def test_document_init(self):
        d = Document(users[0], test_file_1, True)
        self.assertTrue(d.validate())

    def test_sign(self):
        try:
            d = Document(users[0], test_file_1, True)
        except TypeError:
            pass
        else:
            d.sign()
            self.assertTrue(users[0] in d.who_signed())
            self.assertEqual(len(d.who_signed()), 1)

    def test_wrong_file(self):
        try:
            d = Document(users[0], test_file_1, True)
        except TypeError:
            pass
        else:
            d.path = test_file_2
