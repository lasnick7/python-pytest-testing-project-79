import os

import pytest
from page_loader import download
import requests_mock
from pathlib import Path


@pytest.fixture
def example_url():
    return 'https://example.com/simple'


@pytest.fixture
def example_dir(tmp_path):
    directory = tmp_path / "dir"
    directory.mkdir()
    return f"{tmp_path}/dir"


def test_download(example_dir, example_url):
    expected_filename = 'example-com-simple.html'
    expected_path = os.path.join(example_dir, expected_filename)
    html_content = '''
    <html>
      <body>
        <p>example text</p>
      </body>
    </html>
    '''

    with requests_mock.Mocker() as m:
        m.get(example_url, text=html_content)
        filepath = download(example_url, example_dir)

        assert filepath == f"{example_dir}/{expected_filename}"
        assert os.path.exists(expected_path)
        assert len(m.request_history) == 1
        assert m.request_history[0].url == example_url
        assert m.request_history[0].method == 'GET'
        # with open(filepath, encoding='utf-8') as file:
        #     assert file.read() == html_content


def test_download_with_images(example_dir, example_url):
    expected_dirname = 'example-com-simple_files'
    expected_image_filename = 'example-com-assets-professions-python.png'
    expected_filename = 'example-com-simple.html'
    html_content = '''
    <html>
      <body>
         <img src="/assets/professions/python.png"/>
      </body>
    </html>
    '''

    image_url = 'https://example.com/assets/professions/python.png'
    image_path = Path('tests/fixtures/python.png')
    image_content = image_path.read_bytes()

    expected_image_path = os.path.join(example_dir, expected_dirname, expected_image_filename)
    expected_path = os.path.join(example_dir, expected_filename)

    with requests_mock.Mocker() as m:
        m.get(example_url, text=html_content)
        m.get(image_url, content=image_content)
        filepath = download(example_url, example_dir)

        assert filepath == f"{example_dir}/{expected_filename}"
        assert os.path.exists(expected_path)
        assert os.path.exists(expected_image_path)
        downloaded_content = Path(expected_image_path).read_bytes()
        assert downloaded_content == image_content
        with open(filepath, encoding='utf-8') as file:
            html = file.read()
            expected_src = f'src="{expected_dirname}/{expected_image_filename}"'
            assert expected_src in html