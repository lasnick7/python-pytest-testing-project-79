# PageLoader

**PageLoader** is a command-line utility that downloads web pages and saves them locally.  
It stores not only the main HTML page but also all related resources (images, CSS, JS), so that the page can be opened offline — just like a browser’s "Save Page" feature.

## Features
- Download full HTML pages with all linked resources
- Save assets (images, styles, scripts) to a separate directory
- Replace remote links with local ones for offline browsing
- Handle common errors (connection issues, invalid paths, permission errors)
- Logging support with detailed execution info
- CLI progress bar during downloads

## Installation
```bash
make install
```

## Usage
```commandline
page-loader -o /var/tmp https://ru.hexlet.io/courses
```
