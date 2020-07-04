import PyPDF2
import pdfrw
import zlib
# deployed version


class Document:

    # TODO: prohibit changing path and user_id
    def __init__(self, user_id, path, primary=False):
        self.user_id = user_id
        self.path = path
        self.primary = primary
        if primary:
            self.set_up_file()
        else:
            self.validate()

    def get_text(self):
        with open(self.path, 'rb') as pdf_file:
            read_pdf = PyPDF2.PdfFileReader(pdf_file)
            number_of_pages = read_pdf.getNumPages()
            text = ''
            for i in range(number_of_pages):
                page = read_pdf.getPage(i)
                page_content = page.extractText()
                text += page_content
        return text

    @staticmethod
    def get_control_sum(text):
        return str(hex(zlib.crc32(str.encode(text)) & 0xffffffff))

    def is_signed_by(self):
        return True if self.user_id in self.who_signed() else False

    def set_up_meta(self, control_sum):
        writer = pdfrw.PdfWriter()
        for page in pdfrw.PdfReader(self.path).pages:
            writer.addPage(page)
        writer.trailer.Info = pdfrw.IndirectPdfDict(
            Owner=self.user_id,
            ControlSum=control_sum,
            SignedBy=''
        )
        writer.write(self.path)

    def set_up_file(self):
        text = self.get_text()
        control_sum = self.get_control_sum(text)
        trailer = pdfrw.PdfReader(self.path)
        try:
            trailer.Info.Owner = self.user_id
            trailer.Info.ControlSum = control_sum
            trailer.Info.SignedBy = ''
            pdfrw.PdfWriter(self.path, trailer=trailer).write()
        except AttributeError:
            self.set_up_meta(control_sum)
        self.primary = False

    def sign(self):
        trailer = pdfrw.PdfReader(self.path)
        if self.validate():
            signed_by = ' '.join(self.who_signed() + [self.user_id])
            trailer.Info.SignedBy = signed_by
        pdfrw.PdfWriter(self.path, trailer=trailer).write()

    def validate(self):
        trailer = pdfrw.PdfReader(self.path)
        if not(trailer.Info and trailer.Info.ControlSum):
            raise ValueError('Document has never been initialized')
        control_sum = str(trailer.Info.ControlSum)
        if self.get_control_sum(self.get_text()) == \
                control_sum[1:len(control_sum) - 1]:
            return True
        raise ValueError('Document has been changed. Control sum doesnt suit '
                         'the content')

    def who_signed(self):
        trailer = pdfrw.PdfReader(self.path)
        signed_by = trailer.Info.SignedBy
        return signed_by[1:len(signed_by) - 1].split()
