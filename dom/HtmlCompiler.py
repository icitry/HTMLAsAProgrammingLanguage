import os.path
import re
import shutil
import subprocess
from distutils.dir_util import copy_tree
from xml.etree import ElementTree

from defs import Constants


class HtmlCompiler:
    def __init__(self, dom, dest):
        self._dom = dom
        self._dest = dest
        self._call_block_regex = r'<div[ \t\n]*call=\"(\w+\((\w+,)*(\w+)\))\"[ \t\n]*/>'
        self._compiler_dir_path = os.path.join(os.path.curdir, 'compiler')
        self._build_dir_path = os.path.join(os.path.curdir, 'compiler', 'build')

    def _replace_call_block(self, match):
        return '{' + match.group(1) + '}'

    def _write_scripts(self):
        with open(Constants.SVELTE_PAGE_PATH, 'a') as f:
            for script in self._dom['script']:
                if script['type'] == 'jsx':
                    f.write('<script>\n')
                    f.write(r'import Cli from "./Cli.svelte";')
                    f.write(script['script'])
                    f.write('</script>')
                    break

        with open(Constants.SVELTE_PAGE_PATH, 'a') as f:
            for script in self._dom['script']:
                if script['type'] == 'default':
                    f.write(f"<svelte:head>{script['script']}</svelte:head>\n")

    def _write_body(self):
        body_string = ElementTree.tostring(
            self._dom['body'].getroot(), encoding="utf-8").decode("utf-8")

        body_string = re.sub(self._call_block_regex, self._replace_call_block, body_string)
        body_string = re.sub('&gt;', '>', body_string)

        with open(Constants.SVELTE_PAGE_PATH, 'a') as f:
            f.write(body_string)

    def _clean_file(self):
        with open(Constants.SVELTE_PAGE_PATH, 'w') as f:
            f.write('')

    def _create_main_component(self):
        self._clean_file()
        self._write_scripts()
        self._write_body()

    def _build_project(self):
        res = subprocess.run(['npm.cmd', 'run', 'build'],
                             cwd=self._compiler_dir_path,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return
        raise SystemExit('Could not compile. Check for errors!')

    def _delete_dir_contents(self, dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def _copy_build_to_dest(self):
        if os.path.exists(self._dest['path']):
            self._delete_dir_contents(self._dest['path'])
        else:
            os.makedirs(self._dest['path'])

        copy_tree(self._build_dir_path, self._dest['path'])

        os.rename(os.path.join(self._dest['path'], 'index.html'),
                  os.path.join(self._dest['path'], self._dest['filename']))

    def compile(self):
        self._create_main_component()
        self._build_project()
        self._copy_build_to_dest()
