# wenku2epub
Convert light novels on <a href ='https://www.wenku8.net/'>wenku8.net</a> to EPUB format.

Inspired by <a href='https://github.com/chiro2001/Wenku8ToEpub-Online'>Wenku8ToEpub-Online</a>, I decided to write my own Python script to automatically scrape book contents from wenku8 and convert to EPUB format. 

## Installation
### 1. Clone this repo

```bash
git clone git@github.com:yuxuanx1e/wenku2epub.git
```

### 2. Install dependencies

<a href='https://pypi.org/project/cloudscraper/'>cloudscraper</a>

This module is used to bypass Cloudflare anti-bot pages. It's required for making requests to <a href ='https://www.wenku8.net/'>wenku8.net</a> as it is protected by Cloudflare.

Install it with:
```bash
pip install cloudscraper
```
<a href ='https://pypi.org/project/beautifulsoup4//'>BeautifulSoup (from bs4)</a>

BeautifulSoup is part of the beautifulsoup4 library, which is used for web scraping, parsing HTML, and XML documents.

Install it with:
```bash
pip install beautifulsoup4
```

## Usage
To run the script, use the following command:
```bash
python main.py
``` 
You will be prompted to enter the URL of the book index page on <a href ='https://www.wenku8.net/'>wenku8.net</a>. 

After a valid URL has been entered, the script will immediately scrape and convert it to EPUB format if the book only has one volume. 

If the book has mulitiple volumes, the terminal will display a list of all volumes, with an index number corresponding to each volume. You can choose to install one specific volume or a consecutive range of volumes from the list using ``[Num]-[Num]`` syntax, for example use ``0-5`` to install volumes 1 to 6. 

## Debug
Sometimes EPUB can fail to process on <a href='https://play.google.com/books'>Google Play books</a>. When this happens, use a EPUB Validator tool to check for any errors. For example: https://epubcheck.mebooks.co.nz/
## Helpful links
I followed and used some of the code template in this tutorial:
- <a href ='https://steemit.com/utopian-io/@bloodviolet/creating-epub-files-in-python-part-1-getting-the-data'>Creating .epub files in Python - Part 1: Getting the data</a>
- <a href ='https://steemit.com/utopian-io/@bloodviolet/creating-epub-files-in-python-part-2-formatting-the-data'>Creating .epub files in Python - Part 2: Formatting the data</a>
- <a href ='https://steemit.com/utopian-io/@bloodviolet/creating-epub-files-in-python-part-3-the-theory-behind-epub-files'>Creating .epub files in Python - Part 3: The theory behind .epub files</a>
- <a href ='https://steemit.com/utopian-io/@bloodviolet/creating-epub-files-in-python-part-4-creating-the-epub-file'>Creating .epub files in Python - Part 4: Creating the .epub file</a>



