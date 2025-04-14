import win32com.client as win32

class HwpWriter:
    def __init__(self):
        self.hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        if not self.hwp.XHwpDocuments.Count:
            self.hwp.HAction.Run("FileNew")

    def insert_paragraph(self, text, bold=False, italic=False):
        self.hwp.MovePos(3)

        char_shape = self.hwp.HParameterSet.HCharShape
        if bold:
            char_shape.Bold = 1
        else:
            char_shape.Bold = 0
        if italic:
            char_shape.Italic = 1
        else:
            char_shape.Italic = 0

        self.hwp.HAction.Execute("CharShape", char_shape.HSet)

        insert_text = self.hwp.HAction.GetDefault("InsertText", self.hwp.HParameterSet.HInsertText.HSet)
        self.hwp.HParameterSet.HInsertText.Text = text + "\n"
        self.hwp.HAction.Execute("InsertText", self.hwp.HParameterSet.HInsertText.HSet)

    def save(self, output_path):
        self.hwp.SaveAs(output_path)
        self.hwp.Quit()
