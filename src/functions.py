# Contains the functions used by main.py
# Author: Yuxuan Xie
# Version: 1
# Date: 12/ 12/ 2022

# Import dependencies
import requests
from bs4 import BeautifulSoup
import validators
import os
import shutil
from textwrap import dedent
from datetime import datetime

import zipfile
import unicodedata


def scrape_wenku(index_url):
    """
    Scrape book content from https://www.wenku8.net/

    @type index_url: str
    @param index_url: URL to the book index page
    """

    print("scape_wenku: Start web scraping from Wenku...")

    temp_dir = "../temp"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    print("scrape_wenku: Directory '% s' created" % temp_dir)

    # Default location to save files
    index_file = '../temp/index.html'  # File name
    cover_file = '../temp/cover.jpg'

    # Download index page
    download_html(index_url, index_file)

    # Extract title, author, chapter names and links from the index page
    title, author, chapter_list = extract_index(index_url, index_file)

    # Download all chapters
    for chapter_name, chapter_url in chapter_list.items():
        chapter_file = '../temp/' + chapter_name + '.html'
        download_html(chapter_url, chapter_file)

        # Update chapter_list value with filename instead of url
        chapter_list[chapter_name] = chapter_file

    # Check if '插图' chapter exists
    if chapter_list['插图'] is not None:
        print("scrape_wenku: Found '插图' chapter!")

        # Get all image URLs from '插图' chapter
        image_url = extract_images(chapter_list['插图'])

        # Ask user to choose a cover image for the book
        cover_url = choose_cover(image_url)

        # Remove '插图' (last chapter) from the list of chapters
        chapter_list.popitem()

    else:
        # Ask user to manually enter URL to the cover image
        cover_url = get_cover()

    # Download image at specified URL
    download_image(cover_url, cover_file)

    # Clean up each chapter
    for chapter_name, chapter_file in chapter_list.items():
        clean_chapter(chapter_file, chapter_name)

    return title, author, chapter_list


def download_html(html_url, html_file):
    """
    Create a variable that stores the HTML code of the website
    Create a file that has the same name as the "html_file" parameter
    Write the HTML code to the file we've created
    Close the file
    
    @type html_url: str
    @param html_url: URL of page to be scraped
    @type html_file: str
    @param html_file: html temp file name
    """

    print("download_html: Fetching %s ..." % html_url)

    # request.get(link) gets the website
    # .text limits the variable to only html code
    # page stores website's HTML code
    page = requests.get(html_url)

    # Check the status of get() method, see if download was successful
    try:
        page.raise_for_status()
    except Exception as exc:
        print('download_html: There was a problem: %s' % exc)  # Print error msg

    #page.encoding = 'gb2312'  # utf-8 decoding didn't work...
    page.encoding = 'gbk'  # utf-8 decoding didn't work...
    page = page.text

    # Open file in write mode 'w'
    # ut8 encoding is most reliable
    file = open(html_file, 'w', encoding='utf-8-sig')

    # write the content of page variable to the created file
    file.write(page)

    # close the files
    file.close()

    print("download_html: Finish writing to %s" % html_file)


def choose_cover(image_url):
    """
    '插图' chapter found, ask user to select url of image to be used as cover

    @type image_url: str
    @param image_url: url of image to be used as cover
    """

    print("choose_cover: %d image URLs found, please choose one as the cover for the book:" % len(image_url))
    image_url_with_index = [f'{index}. {url}' for index, url in enumerate(image_url)]
    print(*image_url_with_index, sep="\n")

    chosen_index = int(input("Choose index number: "))

    while chosen_index not in range(len(image_url)):
        print("Invalid index number, please choose from 0 to %d" % (len(image_url) - 1))
        chosen_index = int(input("Choose index number: "))

    return image_url[chosen_index]


def get_cover():
    """
    Ask user to manually enter url to the cover image
    """

    print("get_cover: Cannot find '插图' chapter, please manually enter the URL to cover image")

    cover_url = input("URL to cover image: ")

    while validators.url(cover_url) and is_url_image(cover_url):
        print("Invalid URL entered! Please try again")
        cover_url = input("URL to cover image: ")

    return cover_url


def is_url_image(image_url):
    """
    Check if url leads to an image

    @type image_url: str
    @param image_url: url of image to be used as cover
    """

    # Make the request appear like coming from a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 '
                      'Safari/537.36'}

    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url, headers=headers)
    print(r.headers["content-type"])
    if r.headers["content-type"] in image_formats:
        return True
    else:
        print("is_url_image: Entered URL does not lead to an image!")
        return False


def download_image(image_url, image_file):
    """
    Fetch image from a URL link and save to local

    @type image_url: str
    @param image_url: url of image to be used as cover
    @type image_file: str
    @param image_file: file name of cover.jpg
    """

    print("download_image: Fetching %s ..." % image_url)

    # Make the request appear like coming from a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 '
                      'Safari/537.36'}

    response = requests.get(image_url, headers=headers)
    if response.ok:
        img_data = response.content
        with open(image_file, 'wb') as handler:
            handler.write(img_data)
    else:
        print('download_image: ', response)

    print("download_image: Successfully downloaded cover image!")


def extract_images(image_page):
    """
    Extract all image URLs from the '插图' chapter

    @type image_page: str
    @param image_page: html file name containing the '插图' chapter
    """

    print("extract_images: Extracting image URLs from '插图' chapter...")

    # Open file in read mode 'r'
    # The file has been encoded using utf8
    raw = open(image_page, 'r', encoding='utf-8-sig')

    # Create Beautiful soup object
    # html.parser is the built-in parser
    soup = BeautifulSoup(raw, 'html.parser')

    image_url = []

    # Find url to the cover image
    for img in soup.findAll('img'):
        link = img.get('src')
        image_url.append(link)

    raw.close()
    os.remove(image_page)
    print("extract_images: Deleting '插图' chapter...")
    return image_url


def extract_index(index_url, index_file):
    """
    Extract the book title, author and chapter names from the downloaded html file

    @type index_url: str
    @param index_url: url to the index page
    @type index_file: str
    @param index_file: html file name containing the index page
    """

    print("extract_index: Extracting title, author and chapters from %s ..." % index_file)
    # Open file in read mode 'r'
    # The file has been encoded using utf8
    raw = open(index_file, 'r', encoding='utf-8-sig')

    # Create Beautiful soup object
    # html.parser is the built-in parser
    soup = BeautifulSoup(raw, 'html.parser')

    # Book title is located in a div element
    # with id = 'title' 
    # Author is located in a div element
    # with id = 'info'
    # Only one element with this item property, use find()
    title = soup.find(id='title').getText().strip()
    author = soup.find(id='info').getText().strip('作者：').strip()

    # Find all the chapters stored inside <a> tags in a table
    chapters = soup.select('td a')

    chapter_list = {}
    base_link = index_url.replace('index.htm', '')

    for chapter in chapters:
        chapter_list[chapter.getText().strip()] = base_link + chapter.get('href')

    # close the file
    raw.close()

    return title, author, chapter_list


def clean_chapter(chapter_file, chapter_name):
    """
    Clean up the html code in chapter retrieved by the request function

    @type chapter_file: str
    @param chapter_file: HTML file name of downloaded chapter
    @type chapter_name: str
    @param chapter_name: name of the chapter
    """

    print("clean_chapter: Clean up html code in %s ..." % chapter_file)

    # Open file in read mode 'r'
    # The file has been encoded using utf8
    raw = open(chapter_file, 'r', encoding='utf-8-sig')

    # Create Beautiful soup object
    # Parameters: file, parser
    # html.parser is the built-in parser
    soup = BeautifulSoup(raw, 'html.parser')

    # Close the file
    raw.close()

    # The chapter content is located in a div element
    # with id = 'content'
    # Only one element with this item property, use find()
    soup = soup.find(id='content')

    # Create new variable containing only text
    text = soup.text

    # delete the last line
    text = text.replace('本文来自 轻小说文库(http://www.wenku8.com)', '').replace(
        '最新最全的日本动漫轻小说 轻小说文库(http://www.wenku8.com) 为你一网打尽！', '')



    # Prevent wrong formatting, strip white spaces
    text = text.lstrip().rstrip()

    text = text.replace('\n\n\n', '\n<br/>\n<br/>\n')

    # Write text to the final HTML file
    file = open(chapter_file, 'w', encoding='utf-8-sig')

    # In the very first line, we have to write the HTML with the xmlns Attribute.
    # This is required since, by convention, epub files are using the XHTML file format
    file.write('<html xmlns="http://www.w3.org/1999/xhtml">')

    # Place chapter name inside title tags
    # Surrounded by the head tag
    file.write("\n<head>")
    file.write("\n<title>" + chapter_name + "</title>")
    file.write("\n</head>")

    # Write the body
    # Use strong tag on the title
    # Placing <p> at the beginning
    file.write("\n<body>")
    file.write("\n<h2>" + chapter_name + "</h2>" + "\n<p>")
    file.write(text)

    # Close all tags
    file.write("\n</p>")
    file.write("\n</body>")
    file.write("\n</html>")
    file.close()


def create_epub(title, author, chapter_list):
    print("create_epub: starting ...")

    dir_list = ["../book", "../book/META-INF", "../book/OEBPS"]
    for dir in dir_list:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        print("create_epub: Directory '%s' created" % dir)

    # mimetype file (same for every epub)
    file = open("../book/mimetype", 'w')
    file.write("application/epub+zip")
    file.close()

    # container.xml file (same for every epub)
    # Create file inside folder 'META-INF'
    # referenced Content.opf, located inside EPUB folder
    file = open("../book/META-INF/container.xml", 'w')

    file.write(dedent('''\
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
    </container>'''))

    file.close()

    # content.opf file
    file = open("../book/OEBPS/content.opf", 'w', encoding='utf-8-sig')

    # Inside metadata, manifest and spine tag, we insert strings
    index_tpl = dedent("""\
    <?xml version='1.0' encoding='utf-8'?>
    <package unique-identifier="id" version="3.0" xmlns="http://www.idpf.org/2007/opf" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
            %(metadata)s
        </metadata>
        
        <manifest>
            %(manifest)s
        </manifest>
        
        <spine toc="ncx">
            %(spine)s
        </spine>
    </package>""")

    # Create metadata string
    metadata = dedent("""\
    <meta property="dcterms:modified">%(time)s</meta>
    \t\t<meta content="Ebook-lib 0.17.1" name="generator"/>
    \t\t<dc:language>en</dc:language>
    \t\t<dc:identifier id="id">%(novelname)s, %(author)s</dc:identifier>
    \t\t<dc:title>%(novelname)s</dc:title>
    \t\t<dc:creator id="creator">%(author)s</dc:creator>
    \t\t<meta name="cover" content="cover-img"></meta>"""
                      % {"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "novelname": title, "author": author})

    # Create a string that contains the manifest data for the table of content,
    # that will be added at the end of the manifest string.
    toc_manifest = '\t\t<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>\n'
    nav_manifest = '\t\t<item href="nav.xhtml" id="nav" media-type="application/xhtml+xml" properties="nav"/>'

    # enumerate(list) is basically the same as range(len(list)), go through the list that contains the html files
    # i is the loop iterations counter and html is the current html file.
    # os.path.basename(html): the basename of the file. For example '/foo/bar/' would return 'bar'.
    # Add a string to manifest every time we go through the for loop.
    # The first %s will be the file number and the second is the link to the chapter.
    # Since the chapter files are in the same folder as the content file, we can just use the basename.
    # In the spine, we will reference each chapter with the id.
    # In the last line of the loop, write the chapter into the .epub folder
    manifest = '<item href="cover.jpg" id="cover-img" media-type="image/jpeg" properties="cover-image"/>\n'
    manifest += '\t\t<item href="cover.xhtml" id="cover" media-type="application/xhtml+xml"/>\n'
    spine = '<itemref idref="cover" linear="no"/>\n\t\t<itemref idref="nav"/>\n'

    for i, chapter in enumerate(chapter_list.values()):
        manifest += '\t\t<item id="chapter_%s" href="chapter_%s.xhtml" media-type="application/xhtml+xml"/>\n' % (
            i + 1, i + 1)
        spine += '\t\t<itemref idref="chapter_%s"/>\n' % (i + 1)

        shutil.copyfile(chapter, "../book/OEBPS/chapter_%s.xhtml" % (i + 1))

    # Copy the cover image
    shutil.copyfile("../temp/cover.jpg", "../book/OEBPS/cover.jpg")

    # Write content.opf file
    file.write(index_tpl % {
        "metadata": metadata,
        "manifest": manifest + toc_manifest + nav_manifest,
        "spine": spine})

    file.close()

    # table of content file
    file = open("../book/OEBPS/toc.ncx", 'w', encoding='utf-8-sig')

    toc = dedent("""\
    <?xml version='1.0' encoding='utf-8'?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
            <meta content="%(novelname)s, %(author)s" name="dtb:uid"/>
            <meta content="0" name="dtb:depth"/>
            <meta content="0" name="dtb:totalPageCount"/>
            <meta content="0" name="dtb:maxPageNumber"/>
        </head>
        
        <docTitle>
            <text>%(novelname)s</text>
        </docTitle>
        
        <navMap>
    %(navpoints)s
        </navMap>
    </ncx>""")

    navpoints = ''

    for i, (chapter_name, chapter) in enumerate(chapter_list.items()):
        navpoints += '\t\t<navPoint id="chapter_%s">\n' % (i + 1)
        navpoints += '\t\t\t<navLabel>\n'
        navpoints += '\t\t\t\t<text>%s</text>\n' % chapter_name
        navpoints += '\t\t\t</navLabel>\n'
        navpoints += '\t\t\t<content src="chapter_%s.xhtml"/>\n' % (i + 1)
        navpoints += '\t\t</navPoint>\n'

    # Write the toc.xhtml file to epub
    file.write(toc % {"novelname": title,
                      "author": author,
                      "navpoints": navpoints})

    file.close()

    # Create nav.xhtml file
    file = open("../book/OEBPS/nav.xhtml", 'w', encoding='utf-8-sig')

    nav = dedent("""\
    <?xml version='1.0' encoding='utf-8'?>
    <!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
        <head>
            <title>%(novelname)s</title>
        </head>
        <body>
            <nav id="id" role="doc-toc" epub:type="toc">
                <h2>%(novelname)s</h2>
            
                <ol>
    %(ol_content)s
                </ol>
            </nav>
        </body>
    </html>""")
    ol_content = ""

    for i, (chapter_name, chapter) in enumerate(chapter_list.items()):
        ol_content += '\t\t\t\t<li>\n'
        ol_content += '\t\t\t\t\t<a href="chapter_%s.xhtml">%s</a>\n' % (i + 1, chapter_name)
        ol_content += '\t\t\t\t</li>\n'

    file.write(nav % {"novelname": title,
                      "ol_content": ol_content})

    file.close()

    cover_xhtml = dedent("""\
    <?xml version='1.0' encoding='utf-8'?>
    <!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#" lang="en" xml:lang="en">
        <head>
            <title>Cover</title>
        </head>
        <body>
            <img src="cover.jpg" alt="Cover"/>
        </body>
    </html>""")

    file = open("../book/OEBPS/cover.xhtml", 'w')

    file.write(cover_xhtml)
    file.close()

    compress_epub(title)

    # Delete temp folders
    shutil.rmtree("../book", ignore_errors=False, onerror=None)
    shutil.rmtree("../temp", ignore_errors=False, onerror=None)


def compress_epub(title):
    # Create a zipfile with variable name epub
    epub = zipfile.ZipFile('../epub/' + title + ".epub", "w")
    path = "../book"
    length = len(path)

    for root, dirs, files in os.walk(path):
        folder = root[length:]  # path without "parent"
        for file in files:
            epub.write(os.path.join(root, file), os.path.join(folder, file))
    epub.close()
