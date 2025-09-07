import re

def make_slug_from_url(url):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', url.split('//')[-1])
    # print(slug)
    return slug


def make_file_name(slug, format):
    return f"{slug}.{format}"


def make_dir_name(slug, directory):
    return f"{slug}_{directory}"


make_slug_from_url('https://stackoverflow.com/questions/24016988/how-to-extract-slug-from-url-with-regular-expression-in-python')