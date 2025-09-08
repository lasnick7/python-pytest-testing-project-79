import os
import argparse

from page_loader.scripts.download import download_page

def main():
    parser = argparse.ArgumentParser(
        prog='page-loader',
        description='Web page downloader'
    )
    parser.add_argument('url')
    parser.add_argument(
        '-o', '--output',
        metavar='OUTPUT',
        help=f'''output directory (default: '{os.getcwd()}')'''
    )
    args = parser.parse_args()
    url = args.url
    path = args.output
    filepath = download_page(url, path)
    print(filepath)

if __name__ == "__main__":
    main()
