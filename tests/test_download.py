import os

import pytest
import requests.exceptions

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
    html_content = '''<html>
 <body>
  <p>
   example text
  </p>
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
        with open(filepath, encoding='utf-8') as file:
            assert file.read() == html_content


def test_download_with_resources(example_dir, example_url):
    expected_dirname = 'example-com-simple_files'
    expected_filename = 'example-com-simple.html'
    html_content = '''
    <html>
      <head>
        <link rel="stylesheet" media="all" href="/assets/application.css">
        <link rel="stylesheet" media="all" href="https://cdn2.hexlet.io/assets/menu.css">
      </head>
      <body>
         <img src="/assets/professions/python.png"/>
         <script src="https://example.com/packs/js/runtime.js"></script>
         <script src="https://js.stripe.com/v3/"></script>
      </body>
    </html>
    '''
    expected_path = os.path.join(example_dir, expected_filename)

    image_url = 'https://example.com/assets/professions/python.png'
    TEST_DIR = Path(__file__).resolve().parent
    image_path = TEST_DIR / "fixtures" / "python.png"
    image_content = image_path.read_bytes()
    expected_image_filename = 'example-com-assets-professions-python.png'

    link_url = 'https://example.com/assets/application.css'
    link_content = '''body {
      margin: 0
    }'''
    expected_link_filename = 'example-com-assets-application.css'

    script_url = 'https://example.com/packs/js/runtime.js'
    script_content = '''console.log("example script")'''
    expected_script_filename = 'example-com-packs-js-runtime.js'

    expected_image_path = os.path.join(example_dir, expected_dirname, expected_image_filename)
    expected_link_path = os.path.join(example_dir, expected_dirname, expected_link_filename)
    expected_script_path = os.path.join(example_dir, expected_dirname, expected_script_filename)

    with requests_mock.Mocker() as m:
        m.get(example_url, text=html_content)
        m.get(image_url, content=image_content)
        m.get(link_url, text=link_content)
        m.get(script_url, text=script_content)
        filepath = download(example_url, example_dir)

        assert filepath == f"{example_dir}/{expected_filename}"
        assert os.path.exists(expected_path)
        assert os.path.exists(expected_image_path)
        assert os.path.exists(expected_link_path)
        assert os.path.exists(expected_script_path)

        downloaded_image_content = Path(expected_image_path).read_bytes()
        assert downloaded_image_content == image_content
        downloaded_link_content = Path(expected_link_path).read_text()
        assert downloaded_link_content == link_content
        downloaded_script_content = Path(expected_script_path).read_text()
        assert downloaded_script_content == script_content

        with open(filepath, encoding='utf-8') as file:
            html = file.read()
            expected_image_src = f'src="{expected_dirname}/{expected_image_filename}"'
            expected_link_href = f'href="{expected_dirname}/{expected_link_filename}"'
            expected_script_src = f'src="{expected_dirname}/{expected_script_filename}"'
            other_host_link_href = f'href="https://cdn2.hexlet.io/assets/menu.css"'
            other_host_script_src = f'src="https://js.stripe.com/v3/"'
            assert expected_image_src in html
            assert expected_link_href in html
            assert expected_script_src in html
            assert other_host_link_href in html
            assert other_host_script_src in html


@pytest.mark.parametrize('status_code', [404, 500])
def test_status_code_errors(example_dir, status_code, example_url):
    with requests_mock.Mocker() as m:
        m.get(example_url, status_code=status_code)
        with pytest.raises(requests.exceptions.HTTPError):
            download(example_url, example_dir)


# @pytest.mark.parametrize('wrong_path, exception', [
#     (1, TypeError),
# ])
# def test_path_errors(wrong_path, exception, example_url, example_dir):
#     with requests_mock.Mocker() as m:
#         m.get(example_url, text='<html>example</html>')
#         with pytest.raises(exception):
#             download(example_url, wrong_path)


def test_not_create_new_dir(example_url, tmp_path):
    missing = tmp_path / 'missing'
    assert not missing.exists()
    with pytest.raises((FileNotFoundError, NotADirectoryError, PermissionError, TypeError)):
        download(example_url, missing)
    assert not missing.exists()
