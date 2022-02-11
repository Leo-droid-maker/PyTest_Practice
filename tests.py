"""
Commands to work with filters:
pytest tests.py::ClassTest::test_order[-r] - run only one test with argiment -r
pytest -k hidden - run tests that contain string 'hidden' in this name

If we use marker @pytest.mark.<name_of_mark> we can use command:
pytest -m <name_of_mark>
to run only marked tests
Needed to add to pytest.ini:
markers = 
    not_passing
Reverse command: pytest -m "not <name_of_mark>"
-------------------------------------------------------------------------------------
Parallel working.

To run tests parallel, need to install:

pipenv install pytest-xdist

Use command:
pytest -n <number of threads>
pytest -n 2
"""

import shutil
import pytest
import subprocess
import os
from pathlib import Path
import sys
import time
import shlex
import dataclasses


class ClassTest:

    @dataclasses.dataclass
    class TestManager:

        temporary_folder: str

        def create_file(self, filename, text):
            (self.temporary_folder / filename).write_text(text)

        def run_ls(self, argument=""):
            if argument == "":
                result = subprocess.run(['ls', self.temporary_folder], stdout=subprocess.PIPE)
            else:
                result = subprocess.run(['ls', argument, self.temporary_folder], stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8')

    @pytest.fixture
    def test_manager(self, tmp_path):
        return self.TestManager(tmp_path)

        # To work with temporary folders we can use build-in  fixtures's methods - tmp_path

    def expensive_operation(self):
        time.sleep(1)

    def test_list_empty_folder(self, test_manager):
        assert not test_manager.run_ls(), 'Listing an empty folder did not return expected result.'

    @pytest.mark.not_passing
    @pytest.mark.xfail
    def test_ls_with_one_file_incorrect(self, test_manager):
        self.expensive_operation()
        test_manager.create_file("first.txt", "")
        assert not test_manager.run_ls(), 'Listing a folder with one file did not return expected result.'

    def test_ls_with_one_file_correct(self, test_manager):
        test_manager.create_file("first.txt", "")
        assert 'first.txt' in test_manager.run_ls(), 'Listing a folder with one file did not return expected result.'

    def test_list_multiple_files(self, test_manager):
        self.expensive_operation()

        test_manager.create_file("first.txt", "")
        test_manager.create_file("second.doc", "")

        result = test_manager.run_ls()
        print(f'Result: [{result}]')
        assert 'first.txt' in result, 'Listing a folder with multiple files did not return expected result.'
        assert 'second.doc' in result, 'Listing a folder with multiple files did not return expected result.'

    def test_multiple_files_with_hidden(self, test_manager):
        self.expensive_operation()

        test_manager.create_file("first.txt", "")
        test_manager.create_file(".hidden_file", "")
        result = test_manager.run_ls()
        print(f'Result: [{result}]')
        assert 'first.txt' in result, 'Listing a folder with hidden file did not return expected result.'
        assert '.hidden_file' not in result, 'Listing a folder with hidden file did not return expected result.'

    def test_list_multiple_files_with_hidden(self, test_manager):

        test_manager.create_file("first.txt", "")
        test_manager.create_file(".hidden_file", "")
        result = test_manager.run_ls('-a')
        print(f'Result: [{result}]')
        assert 'first.txt' in result, 'Listing a folder with hidden file did not return expected result.'
        assert '.hidden_file' in result, 'Listing a folder with hidden file did not return expected result.'

    # bad way ----------------------------------------------------------------------------------------------------

    def test_order(self, test_manager):

        test_manager.create_file("first.txt", "")
        time.sleep(0.1)
        test_manager.create_file("second.txt", "")

        result = test_manager.run_ls()
        assert result.startswith('first.txt'), 'Output of ls with no arguments was wrong'

        result = test_manager.run_ls('-r')  # -r - reverse
        assert result.startswith('second.txt'), 'Output of ls with -r argument was wrong'

        result = test_manager.run_ls('-t')
        assert result.startswith('second.txt'), 'Output of ls with -t argument was wrong'

        result = test_manager.run_ls('-rt')
        assert result.startswith('first.txt'), 'Output of ls with -rt argument was wrong'

    # good way ----------------------------------------------------------------------------------------------------

    @pytest.mark.parametrize('argument', ['', '-r', '-t', '-rt'])
    def test_order(self, argument, test_manager):
        self.expensive_operation()

        test_manager.create_file("first.txt", "")
        time.sleep(0.1)
        test_manager.create_file("second.txt", "")

        assert test_manager.run_ls(argument).startswith('first.txt' if argument in ['', '-rt'] else 'second.txt'), \
            f'Output of ls with {argument} argument was wrong'


@pytest.mark.not_passing
@pytest.mark.skipif(not sys.platform.lower() == 'windows', reason='Skipping windows-only test')
class WindowsTest:

    @staticmethod
    def test_ls_windows_skipped():
        try:
            os.mkdir('c:\testfolder')
            Path('c:\testfolderfirst.txt').touch()
            result = subprocess.run(['dir', 'c:\testfolder'], stdout=subprocess.PIPE)
            assert 'first.txt' in result.stdout.decode(
                'utf-8'), 'Listing a folder with one file did not return expected result.'
        finally:
            shutil.rmtree('c:\testfolder')
