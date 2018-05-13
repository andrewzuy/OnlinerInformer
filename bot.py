from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote_plus
import sqlite3
import threading
import time
import requests

class OnlinerInformer():

    def __init__(self):
        self.sqlite_file = "database.db"
        self.conn = sqlite3.connect(self.sqlite_file)
        self.c = self.conn.cursor()
        self.c.execute("SELECT TOKEN from TELEGRAM")
        self.token = self.c.fetchall().pop()[0]
        self.telegramBaseUrl = "https://api.telegram.org/bot"+self.token
        self.c.execute("SELECT BASEURL from FORUM WHERE NAME='LithuanianEmbassy'")
        self.forumBaseUrl = self.c.fetchall().pop()[0]
        self.c.execute("SELECT ENDURL from FORUM WHERE NAME='LithuanianEmbassy'")
        self.forumEndUrl = self.c.fetchall().pop()[0]

    # get the contents
    def run_nigger(self):
        response = urlopen(self.forumBaseUrl+self.forumEndUrl)
        doc = response.read()
        soup = BeautifulSoup(doc)
        for post in soup.select("ul.b-messages-thread > li[id]"):
            id = post.attrs['id']
            if self.is_post_new(id):
                print(id)
                print(quote_plus(post.select("div.b-msgpost-txt")[0].text.strip()))
                print(self.post_message(post.select("div.b-msgpost-txt")[0].text.strip()))
        self.update_end_url()

    def post_message(self, message):
        message = quote_plus(message + "\r\n"+ self.forumBaseUrl+self.forumEndUrl)
        clientRequest = requests.request(method="GET", url=self.telegramBaseUrl + "/sendMessage?chat_id=130671039&text=" + message)
        clientRequest = requests.request(method="GET", url=self.telegramBaseUrl + "/sendMessage?chat_id=79694492&text=" + message)
        return clientRequest.status_code

    def is_post_new(self, post):
        self.c.execute("SELECT * from POSTS WHERE POST='"+post+"'")
        result = self.c.fetchall()
        if not result:
            command = "INSERT INTO POSTS(POST) values('" + post + "')"
            self.c.execute(command)
            self.conn.commit()
            return True
        return False

    def update_end_url(self):
        response = urlopen(self.forumBaseUrl+self.forumEndUrl)
        doc = response.read()
        soup = BeautifulSoup(doc)
        if soup.select("li.page-next"):
            self.forumEndUrl = soup.select("li.page-next > a")[0].attrs['href']
            self.forumEndUrl = self.forumEndUrl.replace('./', '/')
            self.update_db_end_url(self.forumEndUrl)

    def update_db_end_url(self,endurl):
        command = "UPDATE FORUM set ENDURL = '"+endurl+"' where NAME='LithuanianEmbassy';"
        self.c.execute(command)
        self.conn.commit()

if __name__ == '__main__':
    lithianianEmbassyInformer = OnlinerInformer()
    while 1 == 1:
        lithianianEmbassyInformer.run_nigger()
        try:
            threading.Thread.start(lithianianEmbassyInformer.run_nigger())
        except:
            print("no updates")
        time.sleep(30)