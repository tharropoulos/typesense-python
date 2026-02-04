import argparse
import filecmp
import os
import re
import shutil
from pathlib import Path

import unasync


ASYNC_DIR = Path("src/typesense/async_")
SYNC_DIR = Path("src/typesense/sync")
CHECK_DIR = Path("src/typesense/sync_check")


def collect_class_replacements(source_dir: Path) -> dict[str, str]:
    replacements: dict[str, str] = {}
    pattern = re.compile(r"^class\s+(Async\w+)", re.MULTILINE)
    for path in source_dir.rglob("*.py"):
        text = path.read_text()
        for match in pattern.finditer(text):
            async_name = match.group(1)
            replacements[async_name] = async_name[len("Async") :]
    replacements["aclose"] = "close"
    return replacements


def collect_files(source_dir: Path) -> list[str]:
    filepaths: list[str] = []
    for root, _, filenames in os.walk(source_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepaths.append(os.path.join(root, filename))
    return filepaths


def run_unasync(output_dir: Path, check: bool = False) -> None:
    source_dir = ASYNC_DIR.resolve()
    target_dir = output_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    replacements = collect_class_replacements(source_dir)
    rule = unasync.Rule(
        fromdir=f"{source_dir.as_posix()}/",
        todir=f"{target_dir.as_posix()}/",
        additional_replacements=replacements,
    )
    filepaths = collect_files(source_dir)
    unasync.unasync_files(filepaths, [rule])

    if check:
        diffs: list[str] = []
        for path in target_dir.rglob("*.py"):
            rel = path.relative_to(target_dir)
            expected = SYNC_DIR / rel
            if not expected.exists():
                diffs.append(f"Missing in sync: {expected}")
                continue
            if not filecmp.cmp(path, expected, shallow=False):
                diffs.append(f"Differs: {expected}")
        if diffs:
            header = [
                "Sync sources are out of date.",
                "Run: uv run python utils/run-unasync.py",
                "",
                "Differences:",
            ]
            raise SystemExit("\n".join([*header, *diffs]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        if CHECK_DIR.exists():
            shutil.rmtree(CHECK_DIR)
        run_unasync(CHECK_DIR, check=True)
        shutil.rmtree(CHECK_DIR)
        return

    run_unasync(SYNC_DIR)


if __name__ == "__main__":
    main()
