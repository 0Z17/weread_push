from notion_client import Client
import logging
import random
from datetime import datetime

class WereadExtractor:
    def __init__(self, token):
        self.notion = Client(auth=token, log_level=logging.ERROR)

        # get the database id
        self.book_database_id = self.get_database_id(self.notion.search(query="书架").get("results"))
        self.mark_database_id = self.get_database_id(self.notion.search(query="划线").get("results"))
        self.note_database_id = self.get_database_id(self.notion.search(query="笔记").get("results"))

        self.mark_cursors = list()
        self.note_cursors = list()

        self.MARK = 0
        self.NOTE = 1

    def get_database_id(self,database_ret):
        """
        Check if the database id is valid.\n
        params:
            database_ret: the return value of notion.search()
        return:
            the database id
        """
        if len (database_ret) == 0:
            print("Database not found.")
            raise Exception("Database not found.")
        
        if len (database_ret) == 1:
            return database_ret[0]["id"]
        
        for i in range(len(database_ret)):
            if database_ret[i]["object"] == "database":
                return database_ret[i]["id"]
        
        print("Database not found.")
        raise Exception("Database not found.")


    def get_mark_info(self, page_id):
        """
        Get the mark info of a page.\n
        params:
            page_id: the id of the page
        return:
            a dictionary containing the mark info {mark_text, book_name, date}
        """

        mark_page = self.notion.pages.retrieve(page_id=page_id)
        mark_text = mark_page.get("properties").get("Name").get("title")[0].get("plain_text")
        
        book_id = mark_page.get("properties").get("书籍").get("relation")[0].get("id")
        book_name = self.get_bookname(book_id)

        date = self.transfer_date(mark_page.get("properties").get("Date").get("date").get("start"))

        return {"mark_text": mark_text, "book_name": book_name, "date": date}
    
    def get_note_info(self, page_id):
        """
        Get the note info of a page.\n
        params:
            page_id: the id of the page
        return:
            a dictionary containing the note info {note_text, content_text, book_name, date}
        """

        note_page = self.notion.pages.retrieve(page_id=page_id)
        note_text = note_page.get("properties").get("Name").get("title")[0].get("plain_text")
        content = note_page.get("properties").get("abstract").get("rich_text")[0].get("plain_text")

        book_id = note_page.get("properties").get("书籍").get("relation")[0].get("id")
        book_name = self.get_bookname(book_id)

        date = self.transfer_date(note_page.get("properties").get("Date").get("date").get("start"))

        return {"note_text": note_text, "content_text": content, "book_name": book_name, "date": date}


    def get_bookname(self, book_id):
        """
        Get the book name of a book.\n
        params:
            book_id: the id of the book
        return:
            the book name
        """
        return self.notion.pages.retrieve(page_id=book_id).get("properties").get("书名").get("title")[0].get("plain_text")

    def transfer_date(self, date):
        """
        Transfer the date format from notion to standard format.\n
        params:
            date: the date in notion format
        return:
            the date in standard format
        """
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
        return dt.strftime('%Y-%m-%d')
    
    def get_number_of_items(self, item_type):
        """
        Get the total number of marks.\n
        return:
            the total number of marks
        """
        if item_type == self.MARK:
            cursor_ls = self.mark_cursors
            database_id = self.mark_database_id
        elif item_type == self.NOTE:
            cursor_ls = self.note_cursors
            database_id = self.note_database_id

        ret = self.notion.databases.query(database_id=database_id)
        has_more = ret.get("has_more")

        number_of_items = len(ret.get("results"))

        while has_more:
            cursor = ret.get("next_cursor")
            cursor_ls.append((cursor, number_of_items))
            ret = self.notion.databases.query(database_id=database_id, start_cursor=ret.get("next_cursor"))
            has_more = ret.get("has_more")
            number_of_items += len(ret.get("results"))

        if item_type == self.MARK:
            print("Total number of marks:", number_of_items)
        elif item_type == self.NOTE:
            print("Total number of notes:", number_of_items)

        return number_of_items


    def get_item_id(self,item_type,idx):
        """
        Get the id of the idx-th item of the specified type.\n
        params:
            item_type: the type of the item (MARK or NOTE)
            idx: the index of the item
        return:
            the id of the idx-th item
        """
        if item_type == self.MARK:
            cursor_ls = self.mark_cursors
            database_id = self.mark_database_id
        elif item_type == self.NOTE:
            cursor_ls = self.note_cursors
            database_id = self.note_database_id

        start_cursor, idx_in_current_list = self.convert_idx(item_type,idx)

        items = self.notion.databases.query(database_id=database_id, start_cursor=start_cursor).get("results")
        return items[idx_in_current_list-1].get("id")
    
    def convert_idx(self,item_type,idx):
        """
        Convert the index of the item to the index of the item in the whole list.\n
        params:
            item_type: the type of the item (MARK or NOTE)
            idx: the index of the item in the whole list
        return:
            start_cursor, idx_in_current_list 
        """
        if item_type == self.MARK:
            cursor_ls = self.mark_cursors
        elif item_type == self.NOTE:
            cursor_ls = self.note_cursors


        # for index smaller than the first cursor
        if idx < cursor_ls[0][1]:
            return None, idx

        for i in range(len(cursor_ls)):
            if idx < cursor_ls[i][1]:
                return cursor_ls[i-1][0], idx-cursor_ls[i-1][1]

        # for index larger than the last cursor
        return cursor_ls[i][0], idx-cursor_ls[i][1]

    def get_random_item(self,item_type,n):
        """
        Get n random items of the specified type.\n
        params:
            item_type: the type of the item (MARK or NOTE)
            n: the number of items to be returned
        return:
            a list of dictionaries containing the info of the random items
        """
        random_idx = random.sample(range(self.get_number_of_items(item_type)-1),n)
        print("Random index:", random_idx)
        item_ls = list()
        for idx in random_idx:
            if item_type == self.MARK:
                item_ls.append(self.get_mark_info(self.get_item_id(item_type,idx)))
            elif item_type == self.NOTE:
                item_ls.append(self.get_note_info(self.get_item_id(item_type,idx)))
        return item_ls
    
    def get_random_marks(self,n):
        return self.get_random_item(self.MARK,n)
    
    def get_random_notes(self,n):
        return self.get_random_item(self.NOTE,n)

if __name__ == '__main__':

    token = "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"
    bm_extractor = WereadExtractor(token)
    print(bm_extractor.get_random_item(bm_extractor.NOTE,5))