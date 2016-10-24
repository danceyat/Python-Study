import json, re
from bs4 import BeautifulSoup

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

soup = BeautifulSoup(html_doc, "html.parser")

#print(soup.prettify())
for tag in soup.find_all(re.compile("^b")):
    print(tag.name)
for tag in soup.find_all(lambda x: x.name.startswith('b')):
    print(tag.name)

soup2 = BeautifulSoup("&ldquo;Dammit!&rdquo; he said.", "html5lib")
print(str(soup2))

print('title' in dir(soup))
print(hasattr(soup, 'title'))
print('title' in soup.__dict__)
print(soup.__getattr__('title'))

markup = "<h1>Sacr\xc3\xa9 bleu!</h1>"
soup = BeautifulSoup(markup, "html5lib")
print(soup.h1)
# <h1>Sacré bleu!</h1>
print(soup.h1.string)
# u'Sacr\xe9 bleu!'
print(soup.original_encoding)
print(soup.contains_replacement_characters)
print(soup.prettify("latin-1"))