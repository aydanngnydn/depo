from openai import OpenAI
import os
import requests
from bs4 import BeautifulSoup
import uuid
from datetime import datetime, timedelta
from googlesearch import search
import shutil
import pickle

whitelist = []

def time_check(content):
    now = datetime.now()
    time_value = content["datetime"]
    return (now - time_value) > timedelta(days=3)

def word_count(text):
    words = text.split()
    return len(words)

def search_website(i):
    urls = search("Business data analytics news")
    j = 0
    for url in urls:
        if j == i:
            return url
        j +=1
 
 
def get_website_content(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    pars = ""
    for par in soup.find_all('p'):
        pars += par.get_text()
    
    return pars

def content_creation(cont):
    stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "write one or two sentences to give context for this text as a md file without writing markdown in the begginning also with a TOML delimiter part which has a title, date and draft=flase values:"+ cont},
              {"role": "user", "content": "explain shortly why the topic in this texts matters as a paragraph in md syntax:"+ cont},
              {"role": "user", "content": "summarize this text using concise words:"+ cont},
              {"role": "user", "content": "give a critical appraisal of the content in:"+ cont},
              {"role": "user", "content": "write a short conlusion about this topic:"+ cont}],
    stream=True,
)
    return stream

def image_creation(cont):
    response = client.images.generate(
    prompt=f"Create an art with this concept:{cont}",
    n=1,
    size="256x256"
    )
    image_url = response.data[0].url
    print(image_url)
    return image_url

def get_title(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        print(lines[1].strip())
        return lines[1].strip()
    
def in_blacklist(file_name, url):
    with open(file_name, 'rb') as file:
            my_list = pickle.load(file)
    if url not in my_list:
        return False
    else:
        return True
    
def append_to_blacklist(file_name, url):
    with open(file_name, 'rb') as file:
            my_list = list(pickle.load(file))
    my_list.append(url)
    with open(file_name, 'wb') as file:
            pickle.dump(my_list, file)



blacklist_filename = "blacklist.pkl"
if not os.path.exists(blacklist_filename):
    blacklist = []
    with open(blacklist_filename, 'wb') as f:
        pickle.dump(blacklist, f)


os.environ["OPENAI_API_KEY"] = "sk--ux-UbzKqCTCxNVsSx8Z4ZBr5FQTxdgSXyXAm7hptMT3BlbkFJWj9-34ypfUmZtPQ6cnAc49X7RndZX5zHgjg2ClmZUA"
client = OpenAI()
i = 0
weburl  = search_website(i)
cont = get_website_content(weburl)
while (cont == "") | (word_count(cont)< 800) | (in_blacklist(blacklist_filename, weburl)== True):
    i+=1
    weburl = search_website(i)
    cont = get_website_content(weburl)


append_to_blacklist(blacklist_filename, weburl)

stream = content_creation(cont)


file_name = uuid.uuid1()
file_path = f"newblog/content/posts/{file_name}.md"

with open(file_path, 'w') as file:
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            file.write(chunk.choices[0].delta.content)



title = get_title(file_path)
image_url = image_creation(title)

response = requests.get(image_url, stream=True)

with open(f'C:/Users/aydan/newblog/content/posts/{file_name}.jpg', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)

del response

with open(file_path, 'a') as file:
    file.write(f"\n\n![image](../{file_name}.jpg)")


with open(file_path, 'a') as file:
    file.write(f"\n\n{weburl}")
