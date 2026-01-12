# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 07:11:34 2020

@author: FykeJ

This utility leverages:
    -the textract module to scan docx, pdf, or other formats, into in-memory utf8 text
    -the natural languange toolkit (nltk) module to split text into a list of sentences
    -the readabilility module to analyze sentence list for readability metrics
The user will need to download each module+dependencies, and additionally, upon first use,
nltk will prompt user to download an additional 'punkt' natural language database.

Use:
    -assign file path/name to file variable
    -run to obtain Fresch Reading Ease and Kincaid Grade Level metrics for text
    
Notes:
    -other metrics are output from readability.getmeasures call
    -other natural language metrics likely give more complex assessments
    -user may want to quickly sanity check 'tokens' list prior to running and/or
     add other filters to code to remove spurious 'sentences' that could impact
     readbaility grades.
"""

import textract    # https://textract.readthedocs.io/en/stable/
import nltk        # https://www.nltk.org/
import readability # https://github.com/andreasvc/readability/

def assess_readability(file):

    text=textract.process(file) # read file
    text=text.decode("utf-8")   # encode in utf-8 https://en.wikipedia.org/wiki/Unicode
    text=text.rstrip()          # strip newline characters from text
    tokens=nltk.tokenize.sent_tokenize(text) # text into sentences
    tokens=[s for s in tokens if not ('\n' in s or '\t' in s)] # additional filter to remove 'sentences' with tabs and newlines.  These are typically headers/titles (e.g. not sentences)

    # Get and display readability stats.
    results=readability.getmeasures(text,lang='en')
    print("FleschReadingEase="+str(int(results["readability grades"]["FleschReadingEase"])))
    print("Kincaid grade level="+str(int(results["readability grades"]["Kincaid"])))

def main():
    #Dummy calls - can modify for real use if required
    print("Yup you're here.")

if __name__ == "__main__":
    main()
