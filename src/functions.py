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


def create_temp_dir():
    """
    Create temporary directories, if directories already exists, then it will be removed
    """

    dir_list = ["../temp", "../book", "../book/META-INF", "../book/OEBPS"]
    for directory in dir_list:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)
        print("create_temp_dir: Directory '%s' created" % directory)


def delete_temp_dir():
    """
    Permanently delete temporary directories
    """

    # Delete temp folders '../book' and '../temp'
    dir_list = ["../temp", "../book"]
    for directory in dir_list:
        shutil.rmtree(directory, ignore_errors=False, onerror=None)
        print("delete_temp_dir: Directory '%s' deleted" % directory)


def scrape_book(volume_name, chapter_list, cover_file):
    """
    Scrape book content from https://www.wenku8.net/ (chapter html and cover image)

    @type volume_name: str
    @param volume_name: Novel name of this volume
    @type chapter_list: dict
    @param chapter_list: chapter names and URLs
    @type cover_file: str
    @param chapter_list: default file location and name for cover image ''../temp/cover.jpg''
    """

    print("scape_book: Start web scraping from Wenku for book '%s' ..." % volume_name)

    # Download all chapters
    for chapter_name, chapter_url in chapter_list.items():
        chapter_file = '../temp/' + chapter_name + '.html'
        download_html(chapter_url, chapter_file)

        # Update chapter_list value with filename instead of url
        chapter_list[chapter_name] = chapter_file

    # Check if '插图' chapter exists
    if '插图' in chapter_list:
        print("scrape_book: Found '插图' chapter!")

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

    return chapter_list


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

    # page stores website's HTML code
    page = requests.get(html_url)

    # Check the status of get() method, see if download was successful
    try:
        page.raise_for_status()
    except Exception as exc:
        print('download_html: There was a problem: %s' % exc)  # Print error msg

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

    while not validators.url(cover_url) or not is_url_image(cover_url):
        print("Invalid URL entered! Please try again")
        cover_url = input("URL to cover image: ")

    return cover_url


def get_index_url():
    """
    Ask user to enter url to the index page of the book
    """

    index_url = input("get_index_url: Please enter URL of the index page of the book:")

    while not validators.url(index_url):
        print("Invalid URL entered! Please try again")
        index_url = input("URL to index page: ")

    return index_url


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
    if r.headers["content-type"] in image_formats:
        print("is_url_image: Success! Entered URL leads to a " + r.headers["content-type"])
        return True
    else:
        print("is_url_image: Entered URL does not lead to an image!")
        return False


def download_image(image_url, image_file):
    """
    Fetch image from a URL link and save to local disk

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
    Extract the book title, author, chapter names and urls from  'index.html' file

    @type index_url: str
    @param index_url: url to the index page
    @type index_file: str
    @param index_file: html file name containing the index page
    """

    print("extract_index: Extracting title, author and volume information from %s ..." % index_file)

    # Open file in read mode 'r'
    raw = open(index_file, 'r', encoding='utf-8-sig')

    # Create Beautiful soup object
    soup = BeautifulSoup(raw, 'html.parser')

    # Book title is located in a div element
    # with id = 'title' 
    # Author is located in a div element
    # with id = 'info'
    title = soup.find(id='title').getText().strip()
    author = soup.find(id='info').getText().strip('作者：').strip()

    # Find all table elements containing either chapter links or volume names
    table_elem = soup.select('td')

    # Remove empty td tags from result set
    tag = '<td class="ccss">\u00a0</td>'
    unwanted = BeautifulSoup(tag, "html.parser").td

    nbsp_count = 0

    for tag in table_elem:
        if tag.text == '\u00a0':
            nbsp_count += 1

    for _ in range(nbsp_count):
        table_elem.remove(unwanted)

    # Get the position of the volume headings
    volume_indices = [i for i, td in enumerate(table_elem) if "vcss" in str(td)]
    volume_indices.append((len(table_elem)))

    # Get volume names
    volume_names = [vol.contents[0] for vol in soup.findAll("td", attrs={'class': "vcss"})]

    # Multiple volumes found
    if len(volume_names) > 1:
        # Ask user to choose which volume(s) to download
        # Update volume indices and names lists to include only wanted volumes
        volume_indices, volume_names = choose_volume(volume_indices, volume_names)

        # Take only the first part of the volume names e.g. '第一卷'
        volume_names = [' ' + name.split()[0] for name in volume_names]

    # Only 1 volume found
    else:
        # Volume name is simply book title, with nothing appended
        volume_names = ['']

    # Store volume name, chapter name and chapter URL in nested dictionary
    volume_chapters = {}
    base_link = index_url.replace('index.htm', '')

    for i in range(len(volume_indices) - 1):
        start_index = volume_indices[i] + 1
        end_index = volume_indices[i + 1]
        chapter_list = {}

        for k in range(start_index, end_index):
            chapter = table_elem[k].a
            chapter_list[chapter.getText().strip()] = base_link + chapter.get('href')

        volume_chapters[title + volume_names[i]] = chapter_list

    raw.close()

    return title, author, volume_chapters


def choose_volume(volume_indices, volume_names):
    """
    Multiple volumes found, ask user to select which volume(s) to download

    @type volume_indices: list
    @param volume_indices: indices of volume names in the table_elem list
     @type volume_names: list
    @param volume_names: volume names
    """

    print("choose_volume: Multiple volumes found! Here is a list of them:")
    volume_info = [f'{index}. {url}' for index, url in enumerate(volume_names)]
    print(*volume_info, sep="\n")
    print("choose_volume: Please choose which volume(s) to download. Input must be single number of a range, e.g. 2-4")
    chosen_indices = input("Enter volume index/indices: ")
    chosen_indices = chosen_indices.split('-')
    chosen_indices = [int(index) for index in chosen_indices]

    while True:
        # Check if entered numbers are within the expected range
        if all(0 <= index < len(volume_names) for index in chosen_indices):
            if len(chosen_indices) == 1:
                break
            # if 'start-end' input format used, make sure start index is less or equal to end index
            elif len(chosen_indices) == 2 and chosen_indices[0] <= chosen_indices[1]:
                break
        # Invalid input, ask for re-enter
        print("Invalid index number, please choose from 0 to %d. Input must be single number or in the form of "
              "'start-end'" % (len(volume_names) - 1))
        chosen_indices = input("Enter volume index/indices: ")
        chosen_indices = chosen_indices.split('-')
        chosen_indices = [int(index) for index in chosen_indices]

    start_volume = chosen_indices[0]

    if len(chosen_indices) == 2:
        end_volume = chosen_indices[1]
    else:
        end_volume = chosen_indices[0]

    # Re-compute the required volume indices and names
    volume_indices = [volume_indices[i] for i in range(start_volume, end_volume + 2)]
    volume_names = [volume_names[i] for i in range(start_volume, end_volume + 1)]

    return volume_indices, volume_names


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
    raw = open(chapter_file, 'r', encoding='utf-8-sig')

    # Create Beautiful soup object
    soup = BeautifulSoup(raw, 'html.parser')

    # Close the file
    raw.close()

    # The chapter content is located in a div element with id = 'content'
    soup = soup.find(id='content')

    # Create new variable containing only text
    text = soup.text

    # delete redundant website messages
    text = text.replace('本文来自 轻小说文库(http://www.wenku8.com)', '').replace(
        '最新最全的日本动漫轻小说 轻小说文库(http://www.wenku8.com) 为你一网打尽！', '')

    # Prevent wrong formatting, strip white spaces
    text = text.lstrip().rstrip()

    # Replace next line characters with br tags
    text = text.replace('\n\n\n', '\n<br/>\n<br/>\n')

    # Write text to HTML file
    file = open(chapter_file, 'w', encoding='utf-8-sig')

    # In the first line, write the HTML with the xmlns Attribute.
    # By convention, epub files are using the XHTML file format
    file.write('<html xmlns="http://www.w3.org/1999/xhtml">')

    # Place chapter name inside title tags
    # Surrounded by the head tag
    file.write("\n<head>")
    file.write("\n<title>" + chapter_name + "</title>")
    file.write("\n</head>")

    # Write the body
    # Use h2 tag on the title
    # Placing <p> at the beginning
    file.write("\n<body>")
    file.write("\n<h2>" + chapter_name + "</h2>" + "\n<p>")
    file.write(text)

    # Close all tags
    file.write("\n</p>")
    file.write("\n</body>")
    file.write("\n</html>")

    # Close file
    file.close()


def create_epub(title, author, chapter_list):
    """
    Create epub file from the retrieved book info and downloaded, cleaned chapters

    @type title: str
    @param title: volume/book title
    @type author: str
    @param author: author name
    @type chapter_list: dict
    @param chapter_list: chapter names and file locations
    """

    print("create_epub: starting ...")

    # mimetype file (same for every epub)
    file = open("../book/mimetype", 'w')
    file.write("application/epub+zip")

    # Close mimetype file
    file.close()

    # container.xml file (same for every epub)
    # Inside folder 'META-INF'
    # referenced Content.opf, located inside OEBPS folder
    file = open("../book/META-INF/container.xml", 'w')

    file.write(dedent('''\
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
    </container>'''))

    # Close container.xml file
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

    # Manifest and spine strings
    manifest = '<item href="cover.jpg" id="cover-img" media-type="image/jpeg" properties="cover-image"/>\n'
    manifest += '\t\t<item href="cover.xhtml" id="cover" media-type="application/xhtml+xml"/>\n'
    spine = '<itemref idref="cover" linear="no"/>\n\t\t<itemref idref="nav"/>\n'

    # Add chapter references to both manifest and spine strings
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

    # Close content.opf file
    file.close()

    # Table of content file 'toc.ncx'
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

    # Add chapter name to table of content
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
    # Close toc.ncx
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

    # Add chapter names
    for i, (chapter_name, chapter) in enumerate(chapter_list.items()):
        ol_content += '\t\t\t\t<li>\n'
        ol_content += '\t\t\t\t\t<a href="chapter_%s.xhtml">%s</a>\n' % (i + 1, chapter_name)
        ol_content += '\t\t\t\t</li>\n'

    file.write(nav % {"novelname": title,
                      "ol_content": ol_content})

    # Close nav.xhtml file
    file.close()

    # Create cover.xhtml
    file = open("../book/OEBPS/cover.xhtml", 'w')

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

    file.write(cover_xhtml)

    # Close cover.xhtml
    file.close()

    # Compress '/book' folder and its content to epub file
    compress_epub(title)

    print("create_epub: Finish EPUB conversion and download for book '%s'!" % title)


def compress_epub(title):
    """
    Compress '/book' folder and its content to epub file

    @type title: str
    @param title: volume/book title
    """

    # Create a zipfile with variable name epub
    epub = zipfile.ZipFile('../epub/' + title + ".epub", "w")
    path = "../book"
    length = len(path)

    for root, dirs, files in os.walk(path):
        folder = root[length:]  # path without "parent"
        for file in files:
            epub.write(os.path.join(root, file), os.path.join(folder, file))
    epub.close()
