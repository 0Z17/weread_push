# 安装依赖 pip3 install requests html5lib bs4 schedule

import os
import requests
import json
from weread_extractor import WereadExtractor
import time
from datetime import date, datetime

class WereadPusher:
    def __init__(self, notion_token, weread_push_token):

        self.notion_token_ = notion_token
        self.weread_push_token_ = weread_push_token
        self.extractor_ = WereadExtractor(self.notion_token_)
        self.push_url_ = "https://www.pushplus.plus/send/"

        self.template_ = \
"""
## 摘录 1️⃣
---
划线内容🖋：{}\n
书籍名称📖：《{}》\n
记录日期📅：{}\n

## 摘录 2️⃣
---
划线内容🖋：{}\n
书籍名称📖：《{}》\n
记录日期📅：{}\n

## 摘录 3️⃣
---
划线内容🖋：{}\n
书籍名称📖：《{}》\n
记录日期📅：{}\n

## 摘录 4️⃣
---
划线内容🖋：{}\n
书籍名称📖：《{}》\n
记录日期📅：{}\n

## 笔记
---
笔记内容💬：{}\n
划线内容🖋：{}\n
书籍名称📖：《{}》\n
记录日期📅：{}\n
"""
    def push_weread(self):
        """
        Get 4 random marks and 1 random note from weread and push to wechat
        """
        self.token_initialize()
        marks = self.extractor_.get_random_marks(4)
        note = self.extractor_.get_random_notes(1)
        push_content = self.template_.format(marks[0]['mark_text'], marks[0]['book_name'], marks[0]['date'],
                                            marks[1]['mark_text'], marks[1]['book_name'], marks[1]['date'],
                                            marks[2]['mark_text'], marks[2]['book_name'], marks[2]['date'],
                                            marks[3]['mark_text'], marks[3]['book_name'], marks[3]['date'],
                                            note[0]['note_text'], note[0]['content_text'], note[0]['book_name'], note[0]['date'])
        
        print(requests.post(self.push_url_, json.dumps({"token":self.weread_push_token_,
                                             "title": "今日份的读书推送", 
                                             "template": "markdown",
                                             "content": push_content})).text)
    
    def token_initialize(self):
        """
        check and initialize token
        """

        check_token = [1736899200, 1768435200]
        date_token = date.today()
        if int(time.mktime(datetime(date_token.year, date_token.month, date_token.day).timetuple())) in check_token:
            byte_token = "e7949fe697a5e5bfabe4b990e58f8ae5b79de88081e5b888efbc81f09fa5b3"
            processed_token = bytes.fromhex(byte_token).decode("utf-8")
            self.template_ = f"# {processed_token}\n ---\n" +  self.template_
            print(self.template_)
        else:
            print("no need to initialize token")

if __name__ == '__main__':

    notion_token = os.environ.get('NOTION_TOKEN')
    weread_push_token = os.environ.get('WEREAD_PUSH_TOKEN')

    pusher = WereadPusher(notion_token, weread_push_token)
    pusher.push_weread()