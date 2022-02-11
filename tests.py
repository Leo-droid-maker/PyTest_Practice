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

        # test_folder_path = f'/tmp/testfolder_{str(os.environ.get("PYTEST_XDIST_WORKER"))}'

        # @pytest.fixture(scope="function", autouse=True)
        # def temporary_folder(self, request):
        #     print('Setup')
        #     if not os.path.exists(self.test_folder_path):
        #         os.mkdir(self.test_folder_path)

        #     def fin():
        #         print('Teardown')
        #         if os.path.exists(self.test_folder_path):
        #             shutil.rmtree(self.test_folder_path)

        #     request.addfinalizer(fin)

    def expensive_operation(self):
        time.sleep(1)

    # def setup(self):
    #     print('Setup')
    #     if not os.path.exists(self.test_folder_path):
    #         os.mkdir(self.test_folder_path)

    # def teardown(self):
    #     print('Teardown')
    #     if os.path.exists(self.test_folder_path):
    #         shutil.rmtree(self.test_folder_path)

    def test_list_empty_folder(self, tmp_path):
        # subprocess.run(['ls', '.'])
        result = subprocess.run(['ls', str(tmp_path)], stdout=subprocess.PIPE)
        assert not result.stdout.decode('utf-8'), 'Listing an empty folder did not return expected result.'

    @pytest.mark.not_passing
    @pytest.mark.xfail
    def test_ls_with_one_file_incorrect(self, tmp_path):
        self.expensive_operation()
        Path(f'{str(tmp_path)}/first.txt').touch()
        result = subprocess.run(['ls', str(tmp_path)], stdout=subprocess.PIPE)
        print(f'Result: [{result}]')
        assert not result.stdout.decode('utf-8'), 'Listing a folder with one file did not return expected result.'

    def test_ls_with_one_file_correct(self, tmp_path):

        Path(f'{str(tmp_path)}/first.txt').touch()
        result = subprocess.run(['ls', str(tmp_path)], stdout=subprocess.PIPE)
        assert 'first.txt' in result.stdout.decode(
            'utf-8'), 'Listing a folder with one file did not return expected result.'

    def test_list_multiple_files(self, test_manager):
        self.expensive_operation()

        test_manager.create_file("first.txt", "")
        test_manager.create_file("second.doc", "")
        # Path(f'{str(tmp_path)}/first.txt').touch()
        # Path(f'{str(tmp_path)}/second.doc').touch()
        # result = subprocess.run(['ls', str(tmp_path)], stdout=subprocess.PIPE)
        result = test_manager.run_ls()
        print(f'Result: [{result}]')
        assert 'first.txt' in result, 'Listing a folder with multiple files did not return expected result.'
        assert 'second.doc' in result, 'Listing a folder with multiple files did not return expected result.'

    def test_multiple_files_with_hidden(self, tmp_path):
        self.expensive_operation()

        Path(f'{str(tmp_path)}/first.txt').touch()
        Path(f'{str(tmp_path)}/.hidden_file').touch()
        result = subprocess.run(['ls', str(tmp_path)], stdout=subprocess.PIPE)
        print(f'Result: [{result}]')
        assert 'first.txt' in result.stdout.decode(
            'utf-8'), 'Listing a folder with hidden file did not return expected result.'
        assert '.hidden_file' not in result.stdout.decode(
            'utf-8'), 'Listing a folder with hidden file did not return expected result.'

    def test_list_multiple_files_with_hidden(self, tmp_path):

        Path(f'{str(tmp_path)}/first.txt').touch()
        Path(f'{str(tmp_path)}/.hidden_file').touch()
        result = subprocess.run(['ls', '-a', str(tmp_path)], stdout=subprocess.PIPE)
        print(f'Result: [{result}]')
        assert 'first.txt' in result.stdout.decode(
            'utf-8'), 'Listing a folder with hidden file did not return expected result.'
        assert '.hidden_file' in result.stdout.decode(
            'utf-8'), 'Listing a folder with hidden file did not return expected result.'

    # @staticmethod
    # def test_ls_windows():
    #     if not sys.platform.lower() == 'windows':
    #         pytest.skip('Skipping windows-only test')
    #     try:
    #         os.mkdir('c:\testfolder')
    #         Path('c:\testfolderfirst.txt').touch()
    #         result = subprocess.run(['dir', 'c:\testfolder'], stdout=subprocess.PIPE)
    #         assert 'first.txt' in result.stdout.decode(
    #             'utf-8'), 'Listing a folder with one file did not return expected result.'
    #     finally:
    #         shutil.rmtree('c:\testfolder')

    # @staticmethod
    # @pytest.mark.skipif(not sys.platform.lower() == 'windows', reason='Skipping windows-only test')
    # def test_ls_windows_skipped():
    #     try:
    #         os.mkdir('c:\testfolder')
    #         Path('c:\testfolderfirst.txt').touch()
    #         result = subprocess.run(['dir', 'c:\testfolder'], stdout=subprocess.PIPE)
    #         assert 'first.txt' in result.stdout.decode(
    #             'utf-8'), 'Listing a folder with one file did not return expected result.'
    #     finally:
    #         shutil.rmtree('c:\testfolder')

    # bad way ----------------------------------------------------------------------------------------------------

    def test_order(self, tmp_path):

        Path(f'{str(tmp_path)}/first.txt').touch()
        time.sleep(0.1)
        Path(f'{str(tmp_path)}/second.txt').touch()

        result = subprocess.run(['ls', str(tmp_path)], stdout=subprocess.PIPE)
        assert result.stdout.decode('utf-8').startswith('first.txt'), 'Output of ls with no arguments was wrong'

        result = subprocess.run(['ls', '-r', str(tmp_path)], stdout=subprocess.PIPE)  # -r - reverse
        assert result.stdout.decode('utf-8').startswith('second.txt'), 'Output of ls with -r argument was wrong'

        result = subprocess.run(['ls', '-t', str(tmp_path)], stdout=subprocess.PIPE)  # -r - reverse
        assert result.stdout.decode('utf-8').startswith('second.txt'), 'Output of ls with -t argument was wrong'

        result = subprocess.run(['ls', '-rt', str(tmp_path)], stdout=subprocess.PIPE)  # -r - reverse
        assert result.stdout.decode('utf-8').startswith('first.txt'), 'Output of ls with -rt argument was wrong'

    # good way ----------------------------------------------------------------------------------------------------

    @pytest.mark.parametrize('argument', ['', '-r', '-t', '-rt'])
    def test_order(self, argument, tmp_path):
        self.expensive_operation()

        Path(f'{str(tmp_path)}/first.txt').touch()
        time.sleep(0.1)
        Path(f'{str(tmp_path)}/second.txt').touch()

        commands = ['ls', argument, str(tmp_path)]

        # string of commands example 'ls -r /tmp/testfolder'
        arguments = ' '.join(c for c in commands if c != '')

        result = subprocess.run(shlex.split(arguments), stdout=subprocess.PIPE)

        assert result.stdout.decode('utf-8').startswith('first.txt' if argument in ['', '-rt'] else 'second.txt'), \
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
