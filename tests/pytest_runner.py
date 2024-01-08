import sys
from pathlib import Path
import pytest

class add_path():
    """
    Add an element to sys.path using a context.
    Thanks to Eugene Yarmash https://stackoverflow.com/a/39855753
    """
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


def main():
    if len(sys.argv) != 1:
        sys.exit(f'usage: {sys.argv[0]}')
    src_path = (Path(__file__).resolve().parent.parent
                / 'src'
                / 'soft_assay_rules'
                )
    with add_path(str(src_path)):
        sys.exit(pytest.main(['-vv', '--ignore=submodules']))


if __name__ == '__main__':
    main()
