import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from page_loader.scripts.validator import validate_path
from page_loader.scripts.utils import (
    make_slug_from_url,
    make_dir_name,
    make_file_name,
    is_absolute_url
)


def download_resource(url, path):
    logger.info(f"Downloading resource: {url}")
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as f:
        f.write(response.content)
    logger.info(f"Resource saved: {path}")


def download_all_resources(resources_tags, url, resourses_dir_path, dirname, attr, target_host, tag):
    for resources_tag in resources_tags:
        src = resources_tag.get(attr)
        if not src:
            continue
        if is_absolute_url(src) and target_host != urlparse(src).netloc:
            continue

        resource_url = urljoin(url, src)
        parsed_resource_url = urlparse(resource_url)
        resource_path, ext = os.path.splitext(parsed_resource_url.path)

        logger.debug(f"{ext}, {not ext}, {tag}")

        if not ext:
            if tag == 'img':
                ext = 'jpg'

            if tag == 'link':
                ext = 'html'

            if tag == 'script':
                ext = 'js'
        else:
            ext = ext.lower()[1:]

        logger.info("LOGGING FOR EXTENSION")
        logger.info(f"URL {resource_url}")
        logger.info(f"PATH {resource_path}, EXT {ext}")


        resource_slug = make_slug_from_url(parsed_resource_url.netloc + resource_path)
        resource_filename = make_file_name(resource_slug, ext)
        resource_filepath = os.path.join(resourses_dir_path, resource_filename)

        try:
            download_resource(resource_url, resource_filepath)
            resources_tag[attr] = f"{dirname}/{resource_filename}"
        except Exception as e:
            logger.warning(f"Error while downloading resource {resource_filename}: {e}")


def download_page(url, output_dir=None):
    logger.info("Starting downloading page")

    if not output_dir:
        output_dir = os.getcwd()

    validate_path(output_dir)

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
    links_tags = html_page.find_all('link')
    scripts_tags = html_page.find_all('script')
    target_host = urlparse(url).netloc

    logger.info("Starting downloading all images")
    download_all_resources(images_tags, url, resourses_dir_path, dirname, 'src', target_host, 'img')
    logger.info("Images were downloaded")
    logger.info("Starting downloading all links")
    download_all_resources(links_tags, url, resourses_dir_path, dirname, 'href', target_host, 'link')
    logger.info("Links were downloaded")
    logger.info("Starting downloading all scripts")
    download_all_resources(scripts_tags, url, resourses_dir_path, dirname, 'src', target_host, 'link')
    logger.info("Scripts were downloaded")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_page.prettify())

    logger.info(f"Page saved: {file_path}")
    return file_path