import win32com.client as win32

class HwpWriter:
    def __init__(self):
        self.hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
        self.hwp.XHwpWindows.Item(0).Visible = True
        self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        self.hwp.Open(r"C:\Users\Suji\Desktop\대표서식1.hwp")  # 고정 템플릿 경로

    def write_all(self, parsed_blocks):
        for block in parsed_blocks:
            if block[0] == 'heading':
                if block[1] == 1:
                    self.hwp.PutFieldText("heading1", block[2])
                if block[1] == 2:
                    self.hwp.PutFieldText("heading2", block[2])
            elif block[0] == 'list':
                if block[1] == 1:
                    self.hwp.PutFieldText("list1", block[2])
                if block[1] == 2:
                    self.hwp.PutFieldText("list2", block[2])
                if block[1] == 3:
                    self.hwp.PutFieldText("list3", block[2])
                if block[1] == 4:
                    self.hwp.PutFieldText("list4", block[2])

    def save(self, path):
        self.hwp.SaveAs(path)

    def quit(self):
        self.hwp.Quit()
