# hwpkit_io.py — HWP/HWPX I/O 통합 (권장 절대경로 + TEMP 저장 + COM 캐시 폴백 포함)
from __future__ import annotations
from pathlib import Path
import os, zipfile, shutil, tempfile

def _safe_hwp_dispatch():
    """
    HWP COM 객체를 안전하게 생성:
    1) EnsureDispatch 시도
    2) gen_py 캐시 삭제/리빌드 후 EnsureDispatch 재시도
    3) Dispatch, 4) ProgID(.1) 폴백
    실패 시 환경 가이드를 포함한 RuntimeError 발생
    """
    import win32com.client as win32
    from win32com.client import gencache

    def _clear_gen_cache():
        try:
            gen_path = gencache.GetGeneratePath()  # venv\Lib\site-packages\win32com\gen_py
            if os.path.isdir(gen_path):
                shutil.rmtree(gen_path, ignore_errors=True)
            gencache.is_readonly = False
            gencache.Rebuild()
        except Exception:
            pass

    # 1) EnsureDispatch
    try:
        return gencache.EnsureDispatch("HWPFrame.HwpObject")
    except Exception:
        _clear_gen_cache()

    # 2) 캐시 초기화 후 EnsureDispatch 재시도
    try:
        return gencache.EnsureDispatch("HWPFrame.HwpObject")
    except Exception:
        pass

    # 3) 동적 Dispatch
    try:
        return win32.Dispatch("HWPFrame.HwpObject")
    except Exception:
        pass

    # 4) 버전 명시 ProgID
    try:
        return win32.Dispatch("HWPFrame.HwpObject.1")
    except Exception as e:
        raise RuntimeError(
            "한/글 COM 객체 생성 실패.\n"
            "- Windows + 한글(Hancom Office) 설치 확인\n"
            "- 파이썬과 한글의 비트수(32/64) 일치 필요\n"
            "- pywin32 설치/재설치: pip install --force-reinstall pywin32"
        ) from e


def convert_hwp_to_hwpx(hwp_path: str, hwpx_path: str) -> None:
    """
    HWP -> HWPX 변환 (절대경로 + 쓰기 가능한 폴더 보장)
    Windows + Hancom Office + pywin32 필요.
    """
    try:
        import win32com.client  # noqa: F401
    except Exception as e:
        raise RuntimeError("pywin32(win32com)가 설치되어야 합니다. pip install pywin32") from e

    # 절대경로로 변환 + 출력 폴더 미리 생성
    hwp_path_abs  = str(Path(hwp_path).resolve())
    hwpx_path_abs = str(Path(hwpx_path).resolve())
    Path(hwpx_path_abs).parent.mkdir(parents=True, exist_ok=True)

    hwp = _safe_hwp_dispatch()
    try:
        hwp.Open(hwp_path_abs)
        hwp.SaveAs(hwpx_path_abs, "HWPX")
    finally:
        try:
            hwp.Quit()
        except Exception:
            pass

    if not Path(hwpx_path_abs).exists():
        raise IOError(f"HWPX 저장 실패: {hwpx_path_abs}")


def convert_hwpx_to_hwp(hwpx_path: str, hwp_out_path: str) -> None:
    """
    HWPX -> HWP 변환 (절대경로 사용)
    Windows + Hancom Office + pywin32 필요.
    """
    try:
        import win32com.client  # noqa: F401
    except Exception as e:
        raise RuntimeError("pywin32(win32com)가 설치되어야 합니다. pip install pywin32") from e

    hwpx_path_abs = str(Path(hwpx_path).resolve())
    hwp_out_abs   = str(Path(hwp_out_path).resolve())
    Path(hwp_out_abs).parent.mkdir(parents=True, exist_ok=True)

    hwp = _safe_hwp_dispatch()
    try:
        hwp.Open(hwpx_path_abs)
        hwp.SaveAs(hwp_out_abs, "HWP")
    finally:
        try:
            hwp.Quit()
        except Exception:
            pass

    if not Path(hwp_out_abs).exists():
        raise IOError(f"HWP 저장 실패: {hwp_out_abs}")


def unzip_hwpx(hwpx_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(hwpx_path), "r") as z:
        z.extractall(out)


def zip_to_hwpx(src_dir: str, out_hwpx_path: str) -> None:
    """
    src_dir(폴더)을 HWPX(zip)으로 묶음.
    """
    src = Path(src_dir)
    out = Path(out_hwpx_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(str(out), "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            z.write(str(p), str(p.relative_to(src)))


def ensure_unzipped_template(template_unzipped_dir: str, base_hwp: str | None) -> str:
    """
    1) template_unzipped_dir가 이미 있으면 그대로 사용
    2) 없고 base_hwp가 있으면 → OS TEMP에 임시 .hwpx 생성 → unzip → 반환
       (한글이 Program Files 아래 기본 폴더를 쓰지 않게 절대경로/TEMP만 사용)
    """
    tud = Path(template_unzipped_dir).resolve()
    if tud.exists():
        return str(tud)

    if base_hwp and Path(base_hwp).exists():
        tmp_hwpx = Path(tempfile.gettempdir()) / ("_tmp_hwpx_" + next(tempfile._get_candidate_names()) + ".hwpx")
        convert_hwp_to_hwpx(str(Path(base_hwp).resolve()), str(tmp_hwpx))
        unzip_hwpx(str(tmp_hwpx), str(tud))
        try:
            tmp_hwpx.unlink(missing_ok=True)
        except Exception:
            pass
        return str(tud)

    raise FileNotFoundError(f"템플릿 폴더 없음: {tud} / base_hwp도 없음: {base_hwp}")
