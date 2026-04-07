#!/usr/bin/env python3
"""compare-screenshots — Compare two sets of screenshots using ImageMagick.

Usage: compare_screenshots.py <baseline-dir> <target-dir> <output-dir>
Requires: ImageMagick (compare, identify commands)
Outputs: Diff images in <output-dir>/diffs/, markdown report to stdout
"""

import shutil
import subprocess
import sys
from pathlib import Path


def check_imagemagick() -> None:
    """Verify ImageMagick is installed."""
    if not shutil.which("compare"):
        print(
            "ImageMagick not installed. Install with: brew install imagemagick",
            file=sys.stderr,
        )
        sys.exit(1)


def get_pixel_count(image_path: str) -> int:
    """Get total pixel count of an image."""
    try:
        result = subprocess.run(
            ["identify", "-format", "%[fx:w*h]", image_path],
            capture_output=True, text=True,
        )
        return int(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return 1


def compare_images(baseline: str, target: str, diff_output: str) -> int:
    """Compare two images, return number of differing pixels."""
    try:
        result = subprocess.run(
            ["compare", "-metric", "AE", baseline, target, diff_output],
            capture_output=True, text=True,
        )
        # ImageMagick writes the metric to stderr
        metric_text = result.stderr.strip()
        return int(metric_text)
    except (subprocess.SubprocessError, ValueError):
        return -1


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: compare_screenshots.py <baseline-dir> <target-dir> <output-dir>",
            file=sys.stderr,
        )
        sys.exit(1)

    baseline_dir = Path(sys.argv[1])
    target_dir = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    diffs_dir = output_dir / "diffs"
    diffs_dir.mkdir(parents=True, exist_ok=True)

    check_imagemagick()

    # Print markdown report header
    print("# Screenshot Comparison")
    print()
    print("| Screenshot | Baseline | Target | Similarity | Diff |")
    print("|------------|----------|--------|------------|------|")

    total = 0
    matched = 0
    baseline_names = set()

    # Compare each baseline image against its target counterpart
    for baseline_img in sorted(baseline_dir.glob("*.png")):
        filename = baseline_img.name
        baseline_names.add(filename)
        target_img = target_dir / filename
        diff_img = diffs_dir / f"diff-{filename}"

        total += 1

        if not target_img.is_file():
            print(f"| {filename} | exists | **missing** | N/A | N/A |")
            continue

        diff_pixels = compare_images(
            str(baseline_img), str(target_img), str(diff_img)
        )
        total_pixels = get_pixel_count(str(baseline_img))

        if diff_pixels == 0:
            matched += 1
            print(f"| {filename} | exists | exists | 100.0% | identical |")
            diff_img.unlink(missing_ok=True)
        elif diff_pixels > 0 and total_pixels > 0:
            similarity = (1 - diff_pixels / total_pixels) * 100
            print(
                f"| {filename} | exists | exists | {similarity:.1f}% "
                f"| [diff](diffs/diff-{filename}) |"
            )
        else:
            print(f"| {filename} | exists | exists | N/A | error |")

    # Report images only in target (new screenshots)
    for target_img in sorted(target_dir.glob("*.png")):
        if target_img.name not in baseline_names:
            print(
                f"| {target_img.name} | **missing** | exists | N/A | new in target |"
            )

    print()
    print(f"**Summary:** {matched}/{total} screenshots identical")


if __name__ == "__main__":
    main()
