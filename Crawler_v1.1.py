#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
import random
import math
import os
import shutil

CRAWL_PROFILE = True
CRAWL_ARTICLE = True
pd.set_option('display.max_colwidth', None)


# In[3]:


seed_url='https://scholar.google.co.uk/citations?view_op=view_org&hl=en&org=9117984065169182779'
base_url='https://scholar.google.co.uk'
articles_inputFile = "C:/Users/ruman/Downloads/Sci-Kit_Learning/7071\CoventryUni_Data_Scraped_articles.csv"

queue= [seed_url]
already_visited=[]
total_entries= 0
last_page_entries =0
profile_id = 1
document_id =1
data_table = {}
article_table = {}

crawl_date = time.ctime()
print(crawl_date)


# # Save crawled data into csv file for later use

# In[4]:


#Write Profile Data into CSV file
def writeData_profile():
    global data_table
    col_names=['Profile_Name','Profile_Link','Designation','Interested_In','No_Of_Citations']

    data_frame=pd.DataFrame.from_dict(data_table,orient ='index',columns=col_names)
    data_frame.index.rename('Profile_Id', inplace=True)
    
    file_exists = os.path.isfile("CoventryUni_Data_Scraped_profile.csv")
    print(file_exists)
    if file_exists: #backup the file
        shutil.copy("CoventryUni_Data_Scraped_profile.csv", "CoventryUni_Data_Scraped_profile_last.csv")  
        
    data_frame.to_csv("CoventryUni_Data_Scraped_profile.csv")


#Write Article Data into CSV file
def writeData_articles():
    global article_table
    col_names=['Profile_Name','Title','All_Authors','Title_Link','No_Of_Citations','Year_Published']

    data_frame=pd.DataFrame.from_dict(article_table,orient='index',columns=col_names)
    data_frame.index.rename('Document_Id', inplace=True)
    
    file_exists = os.path.isfile("CoventryUni_Data_Scraped_articles.csv")
    print(file_exists)
    if file_exists: #backup the file
        shutil.copy("CoventryUni_Data_Scraped_articles.csv", "CoventryUni_Data_Scraped_articles_last.csv") 
        
    data_frame.to_csv("CoventryUni_Data_Scraped_articles.csv")    


# # Extract Next page link

# In[5]:


# returns link of next page
def extract_next_page_link(soup):
    global seed_url
    global total_entries
    #find the html tags for next page from html page
    next_page=soup.find('button',attrs={'aria-label':'Next'})['onclick']

    # extract the keys for next page - 
    next_page_keys= str.split(next_page,sep='\\')[-4:]
    #Append to seed url to navigate to next 
    next_page_link = seed_url+'&'+next_page_keys[0][3:]+"="+next_page_keys[1][3:]+                                "&"+next_page_keys[2][3:]+"="+str(total_entries)

#     print(next_page_keys)
#     print(next_page_link)
    return next_page_link


# # Find all the Names and required information in a page - Main landling page

# In[6]:


#Input :class:`Response <Response>` object from GET request. Update profile information in the data_table

def extract_info_from_page(page):
    global base_url
    global total_entries
    global queue
    global last_page_entries
    global data_table
    global profile_id

    soup = BeautifulSoup(page.content, 'html.parser')
    users= soup.find_all('div',attrs={'class':'gsc_1usr'})
    no_of_entries_in_page = 0
    for user in users:
        profile_name=user.find('h3',attrs={'class':'gs_ai_name'})
        link = user.find('a')['href']
        designation =user.find('div',attrs={'class':'gs_ai_aff'})
        interests = user.find('div',attrs={'class':'gs_ai_int'})
        no_of_citation = user.find('div',{'class':'gs_ai_cby'})
        no_of_entries_in_page +=1

        if no_of_citation.text != '':
            citation = str.split(no_of_citation.text,sep=' ')[2]
        else:
            citation =0
        
        data_table[profile_id] = [profile_name.text,base_url+link,designation.text,interests.text,citation]
        
        profile_id =profile_id+1
        
#         print("User Name: ",name.text)
#         print("Link : ",base_url+link)
#         print("Designation :",designation.text)
#         print("Interests : ",interests.text)
#         print("No.of Citations :",str.split(no_of_citation.text,sep=' ')[2])
#         print("\n")

    if last_page_entries == 0:
        last_page_entries = no_of_entries_in_page

    if no_of_entries_in_page <last_page_entries : # We have reached to last page
        total_entries=total_entries+no_of_entries_in_page
    else:    
        total_entries=total_entries+no_of_entries_in_page
        next_page= extract_next_page_link(soup) # still more pages left
        queue.append(next_page)
        last_page_entries = no_of_entries_in_page


# # Extract individual profile details like Papers published, year etc..- Author Landing Page

# In[7]:


# Input - Profile link
# output - update article_table with all the details related with the profile 
def extract_user_info(profile_url):
    global article_table
    global document_id
    start = 0
    page_size=20    
    #access url of profile 
    page =requests.get(profile_url)   
    
    if page.status_code != 200:
        print("Failed to access url..[ERROR_CODE]:", page.status_code)
        print("Page Url : ",profile_url)
        raise Exception("Error loading page..")

    else:
        #read the page HTML content
        soup = BeautifulSoup(page.content, 'html.parser')
        #find  all the articles on single page
        name = soup.find('div',attrs={'id':'gsc_prf_in'})
        titles = soup.find_all('td',attrs={'class':'gsc_a_t'})
        
#         print(len(name),len(titles))
        while len(titles) > 0: # NOT NULL
        
            no_of_citations = soup.find_all('td',attrs={'class':'gsc_a_c'})
            year_Published = soup.find_all('td',attrs={'class':'gsc_a_y'})          
            
            for title, citation,year in zip(titles,no_of_citations,year_Published):
#                 temp_title=title.find('a').text+" "+title.find('div',attrs={'class':'gs_gray'}).text #title +Authors
                
                profile_name = name.text
#                 print("Profile: ",profile_name)
                title_name = title.find('a').text
#                 print("Title: ",title_name)
                all_authors = title.find('div',attrs={'class':'gs_gray'}).text
#                 print("All authors: ",all_authors)                
                title_link = base_url+title.find('a')['data-href']
#                 print("link: ",title_link)                
                no_Of_Citations = citation.text
#                 print("citation: ",no_Of_Citations)                
                year_published = year.text
#                 print("Year published : ", year_published)
                
                article_table[document_id] = [profile_name,title_name,all_authors,title_link,no_Of_Citations,year_published]

                document_id=document_id+1 # increment the document id for next item
            
            start = start+page_size # show more pages of articles
            if start != 100:
                page_size = 80
            else:
                page_size = 100

            new_page = requests.get(profile_url+'&cstart='+str(start)+'&pagesize='+str(page_size))
            soup = BeautifulSoup(new_page.content, 'html.parser')
            titles = soup.find_all('td',attrs={'class':'gsc_a_t'})

            


# In[8]:


# Test code
page = requests.get(seed_url)
print(page.status_code)


# ## 1. Crawl and extract all the profile related with coventry univertiy authors on google scholar
# ## 2. Crawl and extract all the papers published by those authors from coventry university

# In[9]:


#hard stop after 500 loops to avoid any server overload due to infinite crawling
stop = 500 # Use only for top level of scraping 
start_time = time.time() # measure time taken to scrape data 
failure=False

if CRAWL_PROFILE:
    #1.1 Crawl through all the pages and extract profile links into a list
    print("\n1.Crawling all the pages and extracting profile links ...")
    print("\nSeed URL : ",seed_url)

    while len(queue)!=0 and stop >0:
        try:
            random_time=random.randint(0,1) # genrate random time wait in sec
            #retrieve HTML content of the page
        #     print("url : ",queue[0])
            page =requests.get(queue[0])

            #extract all the requried info from the page
            if page.status_code==200:
                extract_info_from_page(page)
            else:
                print("Failed to load page [ERROR_CODE]: ",page.status_code)
                print("Page Url : ",queue[0])

            #Try next link -> pop out the first page from main queue::FIFO and add into already visited url list
            if len(queue)>0 :
                already_visited.append(queue.pop(0))
            stop = stop-1
            print(".",end='') # print to show that scraping is in progress...
            time.sleep(random_time)  # add delay of 1s before visiting next page
        except:
            print("Inside level 1 crawling....something went wrong..Exiting\n")
            failure=True
            break

    stop_time = time.time()        
    if failure==False:
        time_taken = stop_time-start_time
        print("\nTime taken to scrape Profile data :",str(np.round(time_taken,4))+" sec")
        
        print("\nSaving all the extracted profiles and articles into csv file..")
        #Write profile data into file
        writeData_profile() 
        print("\nSaving Completed.")         
    else:
        time_taken = stop_time-start_time
        print("\nTime taken to scrape Profile data :",str(np.round(time_taken,4))+" sec")
        
        print("\nSaving all the extracted profiles and articles into csv file..")
        #Write profile data into file
        writeData_profile()         
        print("Level 1: Extraction of profiles failed...Saving extracted data so far. Program exit")

if CRAWL_ARTICLE:    
    start_time = time.time() # measure time taken to scrape data 
    #1.2 Crawl through all the profiles link now to extract articles for each users
    profile_df =pd.read_csv("CoventryUni_Data_Scraped_profile.csv",header='infer')
    profile_queue = profile_df['Profile_Link'].values # assign the profile_queue with list of all the pofile link ::FIFO
    head_profile_url = profile_queue[0]
    stop = len(profile_queue)

    print("\nn 2. Crawling all the Profile links and extracting articles info ...")
    print("\nFirst profile link : ",head_profile_url)
    print("\nQueue length : ",len(profile_queue))

    while len(profile_queue) != 0 and stop >0:
        try:
            stop = stop-1
            random_time=random.randint(0,1) # genrate random time wait in sec

               # Crawl to individual user profile and extract their published articles details
            extract_user_info(head_profile_url)
#             print("Processsing done , pending ", len(profile_queue)-1)
                #pop out the first link from the queue and assign second link as first item
            if len(profile_queue)!=1:
                profile_queue = profile_queue[1:]
                #assign head of queue to head_profile_url for next crawl
                head_profile_url = profile_queue[0]
            else:
                profile_queue = [] # All the links are crawled

            print(len(profile_queue),end=',') # print to show that scraping is in progress...
            time.sleep(random_time)  # add delay of 1s before visiting next page
        except:
            print("Inside level 2 crawling....something went wrong..Exiting\n")
            failure = True
            break

    stop_time = time.time()
    if failure == False:
        time_taken = stop_time-start_time
        print("\nTime taken to scrape article data :",str(np.round(time_taken,4))+" sec")

        print("Nothing to process. Queue Len : ",len(queue))
        print("No.Of Entries extracted : ", total_entries)
        print("\nCompleted before hard stop, Iterations still left before hard stop(max 500 iterations) : ",stop)

        #Write published article data into file
        print("\nSaving all the extracted articles details into csv file..")    
        writeData_articles()
        print("\nSaving Completed.")  
    else:
        print("pages pending to crawl : ",len(profile_queue))
        time_taken = stop_time-start_time
        print("\nTime taken to scrape article data :",str(np.round(time_taken,4))+" sec")        
        writeData_articles()
        print("Level 2: Extraction of articles failed.. Saving crawled data so far.. Program exit")
    


# In[ ]:





# In[ ]:




