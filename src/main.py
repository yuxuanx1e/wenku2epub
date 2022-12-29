# This is the main program to generate epub from website
# Author: Yuxuan Xie
# Version: 1
# Date: 12/ 12/ 2022

# Import Dependencies
import functions


def main():
    print("main: Hello World!")
    #index_url = 'https://www.wenku8.net/novel/3/3299/index.htm'
    index_url = 'https://www.wenku8.net/novel/3/3348/index.htm'
    title, author, chapter_list = functions.scrape_wenku(index_url)

    # title = "我想成为你的眼泪"
    # author = "四季大雅"
    # chapter_list = {'序章': '../temp/序章.html', '第一话': '../temp/第一话.html', '第二话': '../temp/第二话.html',
    #                 '第三话': '../temp/第三话.html', '第四话': '../temp/第四话.html', '第五话': '../temp/第五话.html',
    #                 '第六话': '../temp/第六话.html', '第七话': '../temp/第七话.html', '第八话': '../temp/第八话.html',
    #                 '第九话': '../temp/第九话.html', '尾声': '../temp/尾声.html'}

    functions.create_epub(title, author, chapter_list)



# Run main program
if __name__ == "__main__":
    main()
