# Processing Wikipedia data - II: Converting XML dumps from Wikimedia to readable json files

<b> Note: Image parsing is WIP </b>

<p align='center'>
<img src="https://github.com/SwamiKannan/Extracting-categories-in-Wikidumps/blob/main/images/objective.png">
</p>
<br>

## Introduction
This git converts the XML files from <a href="https://en.wikipedia.org/wiki/Special:Export">Wikipedia's Special:Export downloads </a>into a simple JSON file that can be loaded on as a Python dictionary for downstream processing. I have seen a lot of similar Wikidump converters on Github but that were primarily using regex for cleaning up XML files treating the entire document as one giant string. I wasn't too comfortable with such brute force cleaning since the data was actually presented very cleanly as tags in the XMLs and I wanted to use the XML tags to process the data. 

I then came across <a href="https://jamesthorne.com/blog/processing-wikipedia-in-a-couple-of-hours/">this </a> post by <a href="https://jamesthorne.com/">James Thorne</a>. I implemented this post with some tweaks and cleanups to the code. This is an incredible walkthrough and huge credit to him.

## Structure and Metrics
### Construct
The code uses two queues, one multiprocess.Process object, an XML.sax handler custom class and two Thread objects to parallely process a large XML file. 
<ul>
<li>XML.sax.ContentHandler custom object: Parses the XML file for namespace == 0 (articles only), identifies the title and the text tags and puts the content on the aq (Anchor queue named after the <a> tag) queue</li>
<li>multiprocess.Process object: 
  <ol>
  <li>Gets the title and text content from aq </li>
  <li>Cleans the content of redundant markup </li>
  <li>Removes the sections of the body text starting with "Also see" (This indicates the end of the main body of the article)</li>
  <li>Extracts the categories for metadata tagging (helps in LLM setups with RAG architectures)</li>
  <li>Puts (title, text, categories) on the fq queue (File queue) </li>
  </ol>
</li>
<li> Thread 1: Reads the aq and fq queues to display how many files are in each of these queues and how many pages have been parsed (from the XML.sax.ContentHandler custom object's status_count</li>
<li> Thread 2: Extracts the data from the fq queue and writes the content to disk </li>
<li> aq - Queue contains the parsed output of the xml handler</li>
<li> fq - Queue contains the cleaned data that needs to be written to disk</li>
</ul>
  
### Performance
Parses a 127 MB wikidumps xml file with 20000 pages in 63.6 seconds.

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
You can load the output json file into Python and extract the content as a Python dictionary as follows:
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
