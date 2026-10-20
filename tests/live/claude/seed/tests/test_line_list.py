import contextlib
import io
import os
import tempfile
import unittest

import line_list


class NonemptyLinesTests(unittest.TestCase):
    def test_keeps_order_duplicates_case_and_spaces(self):
        text = "pear\n\nApple\n  pear \npear\n   \napple\n"
        self.assertEqual(
            line_list.nonempty_lines(text), ["pear", "Apple", "  pear ", "pear", "   ", "apple"]
        )

    def test_accepts_crlf_and_a_last_line_without_newline(self):
        self.assertEqual(line_list.nonempty_lines("one\r\n\r\ntwo"), ["one", "two"])

    def test_empty_text_has_no_lines(self):
        self.assertEqual(line_list.nonempty_lines(""), [])


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name

    def write(self, data):
        path = os.path.join(self.directory, "input.txt")
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def run_cli(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = line_list.main(list(args))
        return status, output.getvalue(), errors.getvalue()

    def test_prints_nonempty_lines_unchanged(self):
        path = self.write("café\r\n\r\n  Straße \n".encode("utf-8"))
        self.assertEqual(self.run_cli(path), (0, "café\n  Straße \n", ""))

    def test_missing_file_fails(self):
        status, output, errors = self.run_cli(os.path.join(self.directory, "missing.txt"))
        self.assertEqual((status, output), (1, ""))
        self.assertTrue(errors)

    def test_invalid_utf8_fails(self):
        status, output, errors = self.run_cli(self.write(b"ok\n\xff\n"))
        self.assertEqual((status, output), (1, ""))
        self.assertTrue(errors)

    def test_requires_exactly_one_path(self):
        for args in ([], ["one.txt", "two.txt"]):
            with self.subTest(args=args):
                errors = io.StringIO()
                with contextlib.redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
                    line_list.main(args)
                self.assertNotEqual(raised.exception.code, 0)
                self.assertIn("usage", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
