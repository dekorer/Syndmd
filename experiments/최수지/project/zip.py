from pathlib import Path
import zipfile

base_dir = Path(r"C:\project\한글-템플릿3owpml")
output_file = base_dir / "완성된문서.hwpx"

with zipfile.ZipFile(output_file, "w") as zf:
    # mimetype은 반드시 압축 안 되고 맨 앞에 위치해야 함
    zf.write(base_dir / "mimetype", arcname="mimetype", compress_type=zipfile.ZIP_STORED)

    # 나머지 폴더들 압축
    for subdir in ["Contents", "Preview", "META-INF"]:
        for file in (base_dir / subdir).rglob("*"):
            if file.is_file():
                arcname = str(file.relative_to(base_dir))
                zf.write(file, arcname=arcname, compress_type=zipfile.ZIP_DEFLATED)

print("완성된문서.hwpx 생성 완료!")
