import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.github_utils import get_latest_release_version  # noqa: E402
from modules.version import SLANG_VERSION  # noqa: E402


def main():
    latest_tag, latest_version = get_latest_release_version("shader-slang/slang")
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"REQUIRES_UPDATE={int(latest_version > SLANG_VERSION)}", file=fh)
        print(f"LATEST_TAG={latest_tag}", file=fh)
        print(f"BRANCH_NAME={latest_tag}", file=fh)


if __name__ == "__main__":
    main()
