import win32com.client as win32

class HwpWriter:
    def __init__(self):
        self.hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        #같은 이름의 파일 존재시 저장할때 오류발생
        self.hwp.XHwpDocuments.Add(0)
        
    def insert_paragraph(self, text, bold=False, italic=False):
        self.hwp.MovePos(3)

        self.hwp.HAction.GetDefault("InsertText", self.hwp.HParameterSet.HInsertText.HSet)
        self.hwp.HParameterSet.HInsertText.Text = text
        self.hwp.HAction.Execute("InsertText", self.hwp.HParameterSet.HInsertText.HSet)

        self.hwp.HAction.Run("BreakLine")

    def write_block(self, kind, content):
        if kind == "heading":
            self.insert_paragraph(content, bold=True)
        elif kind =="bullet":
            self.insert_paragraph("* " + content)
        elif kind == "hr":
            self.insert_paragraph("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        else:
            self.insert_paragraph(content)

    def save(self, output_path):
        self.hwp.SaveAs(output_path)
