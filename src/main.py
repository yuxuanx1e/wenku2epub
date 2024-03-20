# This is the main program to generate epub from wenku8
# Author: Yuxuan Xie
# Version: 2
# Date: 20/ 03/ 2024

# Import Dependencies
import functions
import os


def main():
    print("main: Starting wenku2epub programme ...")

    # Change to current working directory
    path = os.getcwd()
    os.chdir(path)

    # Ask user to enter the URL to the index page of the book
    index_url = functions.get_index_url()

    # Default location to save files
    index_file = '../temp/index.html'  # File name
    cover_file = '../temp/cover.jpg'

    # Create temp directories
    functions.create_temp_dir()

    # Download index page
    functions.download_html(index_url, index_file)

    # Extract key information from the index.html file
    title, author, volume_chapters = functions.extract_index(index_url, index_file)

    # Loop through each volume
    for i, (volume_name, chapter_list) in enumerate(volume_chapters.items()):

        # Get book contents: chapters and cover image
        chapter_list = functions.scrape_book(volume_name, chapter_list, cover_file)

        # Create epub file
        functions.create_epub(volume_name, author, chapter_list)

        if i == len(volume_chapters) - 1:
            # Delete temp directories
            functions.delete_temp_dir()
        else:
            # Remove and re-create temp directories
            functions.create_temp_dir()

    # Exit message
    print("main: Successfully created and downloaded all epub files, exiting ...")


# Run main program
if __name__ == "__main__":
    main()
