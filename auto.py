import re
import shutil
from pathlib import Path

import pandas as pd

try:
    from zhconv import convert
except ImportError:
    print("警告：未安装 zhconv，将跳过简繁转换搜索。可运行 pip install zhconv 安装。")

    def convert(text, target="zh-hant"):
        return text


BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "歌单.xlsx"
SEARCH_ROOTS = [
    r"D:\Users\Dr.Cai\Downloads",
    
]
OUTPUT_FOLDER_NAME = "音乐搜索结果"
AUDIO_EXTENSIONS = {
    ".mp3",
    ".flac",
    ".wav",
    ".m4a",
    ".ape",
    ".aac",
    ".ogg",
    ".wma",
}
MIN_ORDER_PREFIX_WIDTH = 3


def get_desktop_folder(folder_name=OUTPUT_FOLDER_NAME):
    """在桌面创建结果文件夹。"""
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path("D:/Users/Dr.Cai/Desktop")
    target = desktop / folder_name
    target.mkdir(parents=True, exist_ok=True)
    return target


def normalize_search_roots(root_values):
    """过滤不存在的根目录，并统一转换为绝对路径。"""
    valid_roots = []
    for raw_root in root_values:
        root = Path(raw_root).expanduser()
        if not root.is_absolute():
            root = (BASE_DIR / root).resolve()
        else:
            root = root.resolve()

        if root.exists() and root.is_dir():
            valid_roots.append(root)
        else:
            print(f"跳过不存在的搜索根目录：{root}")
    return valid_roots


def load_song_names(excel_path):
    """按无表头 Excel 读取第一列全部非空歌名。"""
    df = pd.read_excel(excel_path, header=None)
    return [str(value).strip() for value in df.iloc[:, 0].dropna().tolist() if str(value).strip()]


def clean_song_name(song_name):
    """去掉序号和括号中的附加说明，只保留核心歌名。"""
    cleaned = song_name.strip()
    cleaned = re.sub(r"^\s*\d+\s*[.．、)\]]\s*", "", cleaned)
    cleaned = re.sub(r"\s*[（(][^()（）]*[)）]\s*", "", cleaned)
    return cleaned.strip()


def build_search_candidates(song_name):
    """按固定顺序生成搜索候选词。"""
    candidates = []
    cleaned_name = clean_song_name(song_name)
    traditional_name = convert(cleaned_name, "zh-hant")

    for candidate in (song_name.strip(), cleaned_name, traditional_name):
        candidate = candidate.strip()
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def iter_audio_files(root_path):
    """递归遍历指定根目录下的音频文件。"""
    try:
        for file_path in root_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in AUDIO_EXTENSIONS:
                yield file_path
    except PermissionError:
        print(f"无权限访问目录，已跳过：{root_path}")


def search_first_match(song_name, search_roots):
    """在多个根目录中按候选词顺序搜索第一个匹配文件。"""
    candidates = build_search_candidates(song_name)
    lowered_candidates = [candidate.casefold() for candidate in candidates]

    for root in search_roots:
        for file_path in iter_audio_files(root):
            file_stem = file_path.stem.casefold()
            for candidate, lowered_candidate in zip(candidates, lowered_candidates):
                if lowered_candidate in file_stem:
                    return file_path, candidate, root
    return None, None, None


def copy_file_to_folder(source_path, target_folder, order_index, prefix_width):
    """复制文件到结果目录，并用序号前缀保证按 Excel 顺序排序。"""
    prefix = f"{order_index:0{prefix_width}d}_"
    destination = target_folder / f"{prefix}{source_path.name}"
    if destination.exists():
        stem = source_path.stem
        suffix = source_path.suffix
        counter = 1
        while destination.exists():
            destination = target_folder / f"{prefix}{stem}_{counter}{suffix}"
            counter += 1

    shutil.copy2(source_path, destination)
    return destination


def write_report(report_path, lines):
    """用 UTF-8 写入结果清单。"""
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    if not EXCEL_FILE.exists():
        print(f"未找到 Excel 文件：{EXCEL_FILE}")
        return

    search_roots = normalize_search_roots(SEARCH_ROOTS)
    if not search_roots:
        print("没有可用的搜索根目录，请先在 SEARCH_ROOTS 中填写有效的绝对路径。")
        return

    try:
        song_names = load_song_names(EXCEL_FILE)
    except Exception as exc:
        print(f"读取 Excel 失败：{exc}")
        return
    prefix_width = max(MIN_ORDER_PREFIX_WIDTH, len(str(len(song_names))))

    target_folder = get_desktop_folder(OUTPUT_FOLDER_NAME)
    print(f"Excel 文件：{EXCEL_FILE}")
    print("搜索根目录：")
    for root in search_roots:
        print(f"  - {root}")
    print(f"结果文件夹：{target_folder}\n")

    found_names = []
    missing_names = []
    detail_lines = []

    for order_index, original_name in enumerate(song_names, start=1):
        print(f"搜索：{original_name}")
        matched_file, matched_candidate, matched_root = search_first_match(original_name, search_roots)

        if matched_file is None:
            print("  未找到")
            missing_names.append(original_name)
            detail_lines.append(f"{original_name}\t未找到")
            print()
            continue

        copied_file = copy_file_to_folder(matched_file, target_folder, order_index, prefix_width)
        print(f"  找到：{matched_file}")
        print(f"  匹配词：{matched_candidate}")
        print(f"  所属根目录：{matched_root}")
        print(f"  已复制到：{copied_file}")
        found_names.append(original_name)
        detail_lines.append(
            f"{original_name}\t{matched_candidate}\t{matched_file}\t{copied_file}"
        )
        print()

    write_report(target_folder / "已搜到.txt", found_names)
    write_report(target_folder / "未搜到.txt", missing_names)
    write_report(
        target_folder / "搜索结果明细.txt",
        ["原始歌名\t匹配词\t源文件路径\t复制后路径"] + detail_lines,
    )

    print("=" * 50)
    print(f"已搜到：{len(found_names)} 首")
    print(f"未搜到：{len(missing_names)} 首")
    print(f"结果已写入：{target_folder}")


if __name__ == "__main__":
    main()
