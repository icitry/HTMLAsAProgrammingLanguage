import argparse
import os

from colorama import Fore

from dom import DomParser, HtmlCompiler


def parse_args(args):
    src = args.get('src')
    dest = args.get('dest')
    if src is None:
        raise SystemExit('A source file must be provided')
    src = os.path.abspath(src)

    if dest is None:
        filename = os.path.basename(src)
        filename, file_extension = os.path.splitext(filename)
        dest = os.path.join(os.path.curdir, 'out')
        dest = os.path.abspath(dest)
    else:
        dest = os.path.abspath(dest)
        filename = os.path.basename(dest)
        filename, file_extension = os.path.splitext(filename)
        if file_extension != '.html':
            raise SystemExit('Dest file can only be html')

        dest = os.path.dirname(dest)

    return {
        'src': src,
        'dest': {
            'path': dest,
            'filename': f'{filename}{file_extension}'
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', '-s', help="Source file path")
    parser.add_argument("--dest", '-d',
                        help="Destination file path. Default is /out/<src_filename> in current directory")

    args = parser.parse_args()
    args = parse_args(vars(args))

    parser = DomParser(src=args['src'])
    parser.parse()

    compiler = HtmlCompiler(dom=parser.dom, dest=args['dest'])
    compiler.compile()
    print(Fore.GREEN + 'Compiled successfully!')


if __name__ == '__main__':
    main()
