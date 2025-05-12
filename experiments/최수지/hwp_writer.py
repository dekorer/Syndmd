import win32com.client as win32
import os

class HwpWriter:
    def __init__(self):
        self.hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
        self.hwp.XHwpWindows.Item(0).Visible = True
        self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        self.hwp.Open(r"C:\Users\Suji\Desktop\대표서식1.hwp")

    def insert_template(self, template_path):
        if os.path.exists(template_path):
            self.hwp.MovePos(3)
            self.hwp.Insert(template_path, "", "")
        else:
            print(f"템플릿 파일이 존재하지 않습니다: {template_path}")

    def write_all(self, parsed_blocks):
        for block in parsed_blocks:
            if block[0] == 'heading':
                level = block[1]
                content = block[2]
                if 1 <= level <= 3:
                    self.insert_template(rf"C:\Users\Suji\Desktop\제목{level}.hwp")
                    field_name = f"heading{level}"
                    self.hwp.MoveToField(field_name)
                    self.hwp.PutFieldText(field_name, content)

            elif block[0] == 'list':
                level = block[1]
                content = block[2]
                if 1 <= level <= 4:
                    self.insert_template(rf"C:\Users\Suji\Desktop\리스트{level}.hwp")
                    field_name = f"list{level}"
                    self.hwp.MoveToField(field_name)
                    self.hwp.PutFieldText(field_name, content)
            
            elif block[0] == 'paragraph':
                content = block[1]
                self.insert_template(r"C:\Users\Suji\Desktop\문장.hwp")
                self.hwp.MoveToField("paragraph")
                self.hwp.PutFieldText("paragraph", content)

    def save(self, path):
        self.hwp.SaveAs(path)

    def quit(self):
        self.hwp.Quit()
