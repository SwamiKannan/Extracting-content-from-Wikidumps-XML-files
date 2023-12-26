# Wikipedia Scraping 2: Converting XML dumps from Wikimedia to readable json files

<p align='center'>
<img src="https://github.com/SwamiKannan/Extracting-categories-in-Wikidumps/blob/main/images/objective.png">
</p>
<br>

## Introduction
This git converts the XML files from Special:Export downloads into a simple JSON file that can be loaded on as a Python dictionary for downstream processing. I have seen a lot of similar Wikidump converters on Github but that were primarily using regex for cleaning up XML files treating the entire document as one giant string. I wasn't too comfortable with such brute force cleaning since the data was actually presented very cleanly as tags in the XMLs and I wanted to use the XML tags to process the data. 

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
#### Note 2: This script only downloads articles and not other namespaces like: 
a. Template: <a href="https://en.wikipedia.org/wiki/Template:Soviet_Naval_reactor">Example</a>
b. Portal: <a href="https://en.wikipedia.org/wiki/Portal:Biography">Example</a>
c. Talk: <a href="https://en.wikipedia.org/wiki/Wikipedia_talk:About">Example</a>
d. User: <a href="https://en.wikipedia.org/wiki/User:Groggler/sandbox">Example</a>
e. Wikipedia: <a href="https://en.wikipedia.org/wiki/Wikipedia:Meetup/San_Francisco/SPIE_2020">Example</a>


Credit: This code is based on <a href="https://jamesthorne.com/">James Thorne</a>'s post: <a href="https://jamesthorne.com/blog/processing-wikipedia-in-a-couple-of-hours/"> Processing Wikipedia in a few hours on a single PC </a>
