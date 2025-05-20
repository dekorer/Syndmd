import zipfile
import shutil
import os

def package_owpml(template_owpml_path: str, section0_path: str, output_owpml_path: str):
    temp_dir = "owpml_temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    with zipfile.ZipFile(template_owpml_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    target_section_path = os.path.join(temp_dir, "Contents", "section0.xml")
    shutil.copy(section0_path, target_section_path)

    shutil.make_archive("result_owpml", 'zip', temp_dir)
    shutil.move("result_owpml.zip", output_owpml_path)
    shutil.rmtree(temp_dir)

    print(f"OWPML 생성 완료 → {output_owpml_path}")
