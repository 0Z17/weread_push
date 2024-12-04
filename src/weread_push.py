# 安装依赖 pip3 install requests html5lib bs4 schedule

import os
import requests
import json
from weread_extractor import WereadExtractor

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

if __name__ == '__main__':

    notion_token = os.environ.get('NOTION_TOKEN')
    weread_push_token = os.environ.get('WEREAD_PUSH_TOKEN')

    pusher = WereadPusher(notion_token, weread_push_token)
    pusher.push_weread()

