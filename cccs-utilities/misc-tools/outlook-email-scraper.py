# -*- coding: utf-8 -*-
"""
Really specific code... pulls URLs out of Outlook emails.  Could certainly be generalized.  win32.com.client is key tool here.
"""
import os
import re
import win32com.client
from pathlib import Path

folder_path=r'C:\Users\fykej\Desktop\Emerging Climate Services Literature Weekly Digest - Copy'
urls=[]
for f in Path(folder_path).rglob('*.msg'):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    msg=outlook.OpenSharedItem(f)
    regex = re.findall(r"<a href=\"([\s\S]*?)\">", msg.HTMLBody)
    del msg
    if len(regex)>0:
        urls.extend(regex)
for to_remove in ['mailto:laura.vanvliet@canada.ca','mailto:jeremy.fyke@canada.ca']:
    urls = list(filter((to_remove).__ne__, urls))
urls=[url.replace('" target="_blank', '') for url in urls]

print(urls)

with open('urls.txt', 'w') as f:
    for item in urls:
        f.write("%s\n" % item)