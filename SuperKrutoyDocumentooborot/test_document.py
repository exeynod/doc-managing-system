from django.test import TestCase
from documents.document import Document


default_pdf = 'SuperKrutoyDocumentooborot/test_docs/default.pdf'
changed_pdf = 'SuperKrutoyDocumentooborot/test_docs/changed.pdf'
users = [str(i) for i in range(5)]


class DocumentClassTest(TestCase):

    def test_document_init(self):
        d = Document(users[0], default_pdf, True)
        self.assertTrue(d.validate())

    def test_sign(self):
        d = Document(users[0], default_pdf, True)
        d.sign()
        self.assertTrue(users[0] in d.who_signed())
        self.assertEqual(len(d.who_signed()), 1)

    def test_wrong_file(self):
        d = Document(users[0], default_pdf, True)
        d.path = changed_pdf
        self.assertFalse(d.validate())

    def test_sign_que(self):
        d = Document(users[0], default_pdf, True)
        for user in users:
            d = Document(user, default_pdf)
            d.sign()
        self.assertEqual(d.who_signed(), users)

    def test_reset(self):
        d = Document(users[0], default_pdf, True)
        for user in users:
            Document(user, default_pdf).sign()
        self.assertEqual(Document(users[0], default_pdf, True).who_signed(), [])
