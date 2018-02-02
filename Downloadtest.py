
import requests
import urllib

def Download():
    url = 'http://www.shuxue9.com'
    path = 'd:\\'
    title = 'pptTest.ppt'
    downLink = '/download/1667.html'
    file_name = path + title
    u = urllib.request.urlopen(url + downLink)
    f = open(file_name, 'wb')

    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        f.write(buffer)
    f.close()
    print("Sucessful to download" + " " + file_name)


def main():
    Download()

if __name__ == '__main__':
    main()