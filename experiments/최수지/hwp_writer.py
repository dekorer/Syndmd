import win32com.client as win32

class HwpWriter:
    def __init__(self, template_path):
        self.hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
        self.hwp.XHwpWindows.Item(0).Visible = True
        self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(r"C:\Users\Suji\Desktop\대표서식1.hwp")
    
    def write_all(self, parsed_blocks):
        for block in parsed_blocks:
            if block[0] == 'heading':
                if block[1] == 1:
                    hwp.PutFieldText("heading1", block[2])
                if block[1] == 2:
                    hwp.PutFieldText("heading2", block[2])
            elif block[0] == 'list':
                if block[1] == 1:
                    hwp.PutFieldText("list1", block[2])
                if block[1] == 2:
                    hwp.PutFieldText("list2", block[2])
                if block[1] == 3:
                    hwp.PutFieldText("list3", block[2])
                if block[1] == 4:
                    hwp.PutFieldText("list4", block[2])
        hwp.Save()
        hwp.Quit()
