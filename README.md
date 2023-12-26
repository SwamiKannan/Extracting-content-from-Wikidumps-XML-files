# Wikipedia Scraping 2: Converting XML dumps from Wikimedia to readable json files

<p align='center'>
<img src="https://github.com/SwamiKannan/Extracting-categories-in-Wikidumps/blob/main/images/objective.png">
</p>
<br>

## Introduction
This git converts the XML files from <a href="https://en.wikipedia.org/wiki/Special:Export">Wikipedia's Special:Export downloads </a>into a simple JSON file that can be loaded on as a Python dictionary for downstream processing. I have seen a lot of similar Wikidump converters on Github but that were primarily using regex for cleaning up XML files treating the entire document as one giant string. I wasn't too comfortable with such brute force cleaning since the data was actually presented very cleanly as tags in the XMLs and I wanted to use the XML tags to process the data. 

I came across <a href="https://jamesthorne.com/blog/processing-wikipedia-in-a-couple-of-hours/">this </a> post by <a href="https://jamesthorne.com/">James Thorne</a>'s post. I implemented his blog post with some tweaks and cleanups to the code. This is an incredible walkthrough and huge credit to him.

## How to run the code:
### 1. Download the repo
```
git clone https://github.com/SwamiKannan/Extracting-categories-in-Wikidumps.git
```
### 2. Run the code:
1. Navigate the src folder inside the git repo just downloaded through the command prompt
2. Run the code:
```
python wiki_explore.py <insert path to Wikdumps xml file including the name of the xml file> --output <path to save the output json file> (If no output is given, the output will be stored in the src directory as "output.json"
```
#### Note 1: Wikdumps files are either in .xml formats or .xml.bz2 formats. This code only opens these two files.
#### Note 2: This script only downloads articles [namespace = 0] and not other namespaces like:
<ol>
  <li>Template: <a href="https://en.wikipedia.org/wiki/Template:Soviet_Naval_reactor">Example</a></li>
  <li>Portal: <a href="https://en.wikipedia.org/wiki/Portal:Biography">Example</a></li>
  <li>Talk: <a href="https://en.wikipedia.org/wiki/Wikipedia_talk:About">Example</a></li>
  <li>User: <a href="https://en.wikipedia.org/wiki/User:Groggler/sandbox">Example</a></li>
  <li>Wikipedia: <a href="https://en.wikipedia.org/wiki/Wikipedia:Meetup/San_Francisco/SPIE_2020">Example</a></li>
</ol>

The script also does not convert pages which are redirect pages i.e. old pages that when you visit re-direct to another page with the latest data. These are pages with the <redirect=""> tags

## Usage:
You can load the json file and extract the content as a Python dictionary as follows:
```
dict_files=[]
with open(<path/filename.json for output file>), encoding='utf-8') as f:
  for line in f:
    line_dict=json.loads(line)
    dict_files.append(line_dict)
```

This gives us a list of dictionaries. Each dictionary has three keys: 
1. page: Page title of the article
2. sentences: Actual content in the article
3. categories: Categories that this article belongs to


## Credits:
1. This code is based on <a href="https://jamesthorne.com/">James Thorne</a>'s post: <a href="https://jamesthorne.com/blog/processing-wikipedia-in-a-couple-of-hours/"> Processing Wikipedia in a few hours on a single PC </a>
2. The cleaner function based on regex from <a href="https://github.com/CyberZHG"> CyberZHG</a>'s <a href="https://github.com/CyberZHG/wiki-dump-reader/blob/master/wiki_dump_reader/cleaner.py">Git repo</a>
