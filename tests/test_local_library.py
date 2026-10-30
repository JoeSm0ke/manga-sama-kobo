import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("library", Path(__file__).parents[1] / "bridge" / "local_library.py")
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)

class LibraryTests(unittest.TestCase):
    def test_library_and_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "series").mkdir()
            book = root / "series" / "volume.cbz"
            book.write_bytes(b"sample")
            self.assertEqual(lib.files_in_library(root), [book])
            self.assertEqual(lib.lookup(root, "series/volume.cbz"), book)
            for candidate in ("../volume.cbz", "/etc/passwd", "series/../../secret.cbz", "series\\volume.cbz", "series//volume.cbz"):
                self.assertIsNone(lib.lookup(root, candidate))
            self.assertIsNone(lib.lookup(root, "missing.cbz"))
            self.assertIsNone(lib.lookup(root, "series/volume.txt"))
            (root / "series" / "volume.txt").write_bytes(b"not a CBZ")
            self.assertIsNone(lib.lookup(root, "series/volume.txt"))
            try:
                (root / "linked.cbz").symlink_to(book)
            except (OSError, NotImplementedError):
                pass
            else:
                self.assertIsNone(lib.lookup(root, "linked.cbz"))
                self.assertNotIn(root / "linked.cbz", lib.files_in_library(root))

if __name__ == "__main__":
    unittest.main()
