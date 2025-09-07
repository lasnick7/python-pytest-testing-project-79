import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


from page_loader.scripts.utils import (
    make_slug_from_url,
    make_dir_name,
    make_file_name
)


def download_image(url, path):
    logger.info(f"Downloading image: {url}")
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as f:
        f.write(response.content)
    logger.info(f"Image saved: {path}")


def download_page(url, output_dir=None):
    logger.info("Startind downloading")
    if not output_dir:
        output_dir = os.getcwd()

    response = requests.get(url)
    response.raise_for_status()

    slug = make_slug_from_url(url)
    filename = make_file_name(slug, 'html')
    file_path = os.path.join(output_dir, filename)

    dirname = make_dir_name(slug, 'files')
    resourses_dir_path = os.path.join(output_dir, dirname)
    os.makedirs(resourses_dir_path, exist_ok=True)

    html_page = BeautifulSoup(response.text, 'html.parser')
    images_tags = html_page.find_all('img')

    for images_tag in images_tags:
        src = images_tag.get('src')
        if not src:
            continue

        image_url = urljoin(url, src)
        parsed_image_url = urlparse(image_url)
        image_path, ext = os.path.splitext(parsed_image_url.path)
        ext = (
            ext.lower()[1:]
            if ext.lower()[1:] in ['jpg', 'jpeg', 'png']
            else 'png'
        )
        image_slug = make_slug_from_url(parsed_image_url.netloc + image_path)
        image_filename = make_file_name(image_slug, ext)
        image_filepath = os.path.join(resourses_dir_path, image_filename)

        try:
            download_image(image_url, image_filepath)
            images_tag['src'] = f"{dirname}/{image_filename}"
        except Exception as e:
            logger.warning(f"Error while downloading image {image_filename}: {e}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_page.prettify())

    logger.info(f"Page saved: {file_path}")
    return file_path