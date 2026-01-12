from pyzotero import zotero
from pathlib import Path
import os
import glob
import pandas as pd

def define_library():
    #Make a new library
    library_id=2913332
    library_type='group'
    api_key='O1VrYbMjMpebFe2yk0soE2xP'
    return zotero.Zotero(library_id, library_type, api_key)

def create_new_item_from_shared_drive(zot):
    #Unsafe code snippets to make new items in an existing library
    ## Create new items in library, based on shared drive items and directories
    input_path="Z:/14-KNOWLEDGE SHARING"
    ##Get list of all documents in shared drive folder and add to Zotero sub-collections.
    shared_drive_dirs=os.listdir(input_path)
    tmp=zot.create_collections([{"name":"shared-drive-contents"}])
    collection_key=tmp["successful"]["0"]["key"]
    for c in shared_drive_dirs:
        tmp=zot.create_collections([{"name":c,"parentCollection":collection_key}])
        subcollection_key=tmp["successful"]["0"]["key"]
        files=glob.glob(os.path.join(input_path,c)+"/*.pdf")
        for f in files:
            print(f)
            item=zot.item_template('report')
            item["title"]=os.path.basename(f)
            item=zot.create_items([item]) #create new item
            item_key=item["successful"]["0"]["key"]
            zot.addto_collection(subcollection_key,item["successful"]["0"]) #add to specific collection corresponding to old folder
            zot.attachment_simple([f],item_key) #attach file

def assign_tags(zot):
    #Half-baked code to do batch tag work
    #Get list of tags from Excel file:
    tags=pd.read_excel(r'Zotero-tags.xlsx')
    tag_list=tags['Tags'].tolist()
    # Get master tag note item
    # Assign all tags to this item
    # Update item (so, all tags will be imported this way into Zotero)
    tag_note=zot.items(q='master-tag-note')
    tag_note=zot.add_tags(tag_note[0],*tag_list)

def scrape_email():
    from win32com.client import Dispatch
    import re
    from urllib.parse import urlparse, parse_qs

    doi_list=[]
    
    # Initialize API to Outlook email folder
    outlook = Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)
    # Set relative path from inbox to folder where Digest emails reside
    messages=inbox.Folders.Item("Projects").\
                   Folders.Item("Weekly Digest").Items
    #Loop over messages in folder, and within Digest emails, find URLs that include 'doi.org'
    for m in messages:
        if m.subject=="Emerging Climate Services Literature: Weekly Digest":
            urls=re.findall(r'(https?://\S+)', m.body)
            for url in urls:
                if url: 
                    safelink_parse_object = parse_qs(urlparse(url).query)
                    if safelink_parse_object:
                        DOI=safelink_parse_object['url'][0]
                        if 'doi.org' in DOI:
                            doi_list+=[DOI]
    return doi_list

def doi2bibtex(doi):
    import sys
    import urllib.request
    import bibtexparser
    from urllib.error import HTTPError
    
    BASE_URL = ''
    
    url = BASE_URL + doi
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/x-bibtex')
    try:
        with urllib.request.urlopen(req) as f:
            bibtex = f.read().decode()
            # The round-trip through bibtexparser adds line endings.
            #bibtex = bibtexparser.loads(bibtex)
            #bibtex = bibtexparser.dumps(bibtex)
            return(bibtex)
    except HTTPError as e:
        if e.code == 404:
            print('DOI not found.')
        else:
            print('Service unavailable.')
        sys.exit(1)

def main():
    #Dummy calls - can modify for real use if required
    print("Yup you're here.")

if __name__ == "__main__":
    main()


