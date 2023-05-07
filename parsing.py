from pykml import parser

from lxml import etree, objectify
import json

# Collected imports
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.text import Text

# Collect additional resources that will be needed
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

# with open("map.kml") as f:
#     document: etree.ElementTree = parser.parse(f)

# root: etree.Element = document.getroot()

# descriptions = []
# found = 0
# def depth_first_print(element: etree.Element):
#     for child in element.iterchildren():
#         depth_first_print(child)
#         if(hasattr(child, 'description')):
#             descriptions.append(child.description)
#             found += 1
#             print(f"Found {found}")

# # root.Document.Folder.Placemark.description has _a_ description, what about all?

# depth_first_print(root)

# Seems to be easier to just parse the string directly instead of dealing with kml tree.
#  - Will require manual cleaning anyway.

with open("map.kml") as f:
    lines = f.readlines()

raw_descriptions = [line.strip() for line in lines if 'description' in line]

# Input Cleaning before combining as a text corpus:

# Starts with '<description><![CDATA['
# First trim '<description>'
# front_desc_trim = [l.split('<description>')[1] for l in raw_descriptions]
front_desc_trim = [line.replace('<description>', '') for line in raw_descriptions]

# Then trim '<![CDATA[' if present
# front_trim = [l.split('<![CDATA[')[1] for l in front_desc_trim if '<![CDATA[' in l else l]
front_trim = [line.replace('<![CDATA[', '') for line in front_desc_trim]
# Ends with ']]></description>'
rear_trim = [line.replace('</description>', '') for line in front_trim]
full_trim = [line.replace(']]>', '') for line in rear_trim]

# This seems good enough to at least get to the processing part but there are various XML
#   escape sequence representations in it. Maybe substitute for another method later.

# requires: nltk.download('punkt')
# Seems like to need to clean this up (lots of bogus tokens)
tokenized_descriptions = [word_tokenize(line) for line in full_trim]


# requires: nltk.download('wordnet')
# requires: nltk.download('omw-1.4')
def lemmatizer_list(lines: list[str]):
    lemmatizer = WordNetLemmatizer()
    new_lines = []
    for line in lines:
        lemmatized_line = [lemmatizer.lemmatize(word) for word in line]
        print(lemmatized_line)
        breakpoint()
        new_lines.append(lemmatized_line)
    return new_lines


# May be interesting to try tagging word parts
lemmatized_token_lines = lemmatizer_list(tokenized_descriptions)

# Try to chunk to look at noun phrases?

# Ideas
#   - trim puncutation
#   - look at most common words (by frequency) [not stop words]
#   - look at concordence of these words!

all_together: str = ""

# Make all lines into one long corpus (str
for line in full_trim:
    all_together += line

all_together = all_together.replace("<br>", " ")
all_together = all_together.replace("\t", " ")
all_together = all_together.replace("\xa0", " ")

text = Text(word_tokenize(all_together))

# Requires: nltk.download('stopwords')
# text.collocations(num=50, window_size=2)
# text.collocations(num=50, window_size=3)

output = {}

# Manually determined keywords for concordance analysis.
keywords = ["he", "his", "calls", "been", "free", "wears", "face",
            "she", "her", "years", "brother", "sister", "child",
            "father", "mother", "feet", "live", "lives"]

for word in keywords:
    # Generate concordance lists for each of our keywords
    output[word] = text.concordance(word, width=70, lines=200)
    # These will have some duplicates and will be manually curated for best presentation.

# Dump output to a text file for manual manipulation.
with open("output.json", "w+") as f:
    f.write(json.dumps(output))
