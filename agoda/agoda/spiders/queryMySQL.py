import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta
from agoda.items import AgodaReviewItem
import sys
import string

class connectMySQL:
    DB_NAME = 'agoda2'
    TABLES = {}
    TABLES['review'] = (
        "CREATE TABLE IF NOT EXISTS `review` ("
        "  `rev_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `title` varchar(255) CHARACTER SET utf8,"
        "  `text` text CHARACTER SET utf8,"
        "  `detect_lang` varchar(10),"
        "  `published_date` bigint(15),"
        "  `published_date_1` date,"

        "  `product_id` int(11),"
        "  `rating` float,"
        "  `rating_outof` varchar(20),"
        "  `author` varchar(255),"
        "  `country` varchar(255),"

        "  `reviewer_group` varchar(255),"
        "  `room_type` varchar(255),"
        "  `stay_detail` varchar(255),"
        "  `url` varchar(255),"
        "  `data_provider_id` int(11),"
        "  `product_name` varchar(255),"
        "  PRIMARY KEY (`rev_no`)"
        ") ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_general_ci")

    TABLES['city'] = (
        "CREATE TABLE IF NOT EXISTS `city` ("
        "  `city_id` varchar(15) NOT NULL,"
        "  `city_name` varchar(255),"
        "  PRIMARY KEY (`city_id`)"
        ") ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_general_ci")
    TABLES['hotel'] = (
        "CREATE TABLE IF NOT EXISTS hotel ("
        "  hotel_id varchar(15),"
        "  hotel_name varchar(255),"
        "  url varchar(255),"
        "  last_date_crawl date,"
        "  PRIMARY KEY (hotel_id)"
        ") ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_general_ci")
    def __init__(self):
        config = {
            'user': 'root',
            'password': 'root',
            'host': '127.0.0.1',
            'raise_on_warnings': True,
        }
        self.cnx = 0
        self.cursor = 0
        try:
            self.cnx = mysql.connector.connect(**config)
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def create_database(self):
        try:
            self.cursor.execute(
                "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(self.DB_NAME))
        except mysql.connector.Error as err:
            print(err)
        self.selectDB()
    def selectDB(self):
        try:
            self.cursor.execute(
                "USE {}".format(self.DB_NAME))
        except mysql.connector.Error as err:
            print(err)
            exit(1)
    def create_table(self):
        for name, ddl in self.TABLES.iteritems():
            try:
                print("Creating table {}: ".format(name))
                self.cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")
    def insert_hotel(self, hotelId, hotelName, url, lastDateCrawl):
        add_hotel = ("INSERT INTO hotel "
              "(hotel_id, hotel_name, url, last_date_crawl) "
              "VALUES (%(hotel_id)s, %(hotel_name)s, %(url)s, %(last_date_crawl)s)")
        data_hotel = {
          'hotel_id': hotelId,
          'hotel_name': hotelName,
          'url': url,
          'last_date_crawl': lastDateCrawl,
        }
        try:
            self.cursor.execute(add_hotel, data_hotel)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print(err)
        else:
            print("Insert Hotel OK !!!")
    def insert_city(self, cityId, cityName):
        add_city = ("INSERT INTO city "
              "(city_id, city_name) "
              "VALUES (%(city_id)s, %(city_name)s)")
        data_city = {
          'city_id': cityId,
          'city_name': cityName,
        }
        try:
            self.cursor.execute(add_city, data_city)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print(err)
        else:
            print("Insert City OK !!!")
    def insert_review(self, it):
        item = it.load_item()
        add_review = ("INSERT INTO review "
              "(title, text, detect_lang, published_date_1, published_date, product_id, rating, rating_outof, author, country, reviewer_group, room_type, stay_detail, url, data_provider_id, product_name) "
              "VALUES (%(title)s, %(text)s, %(detect_lang)s, %(published_date_1)s, %(published_date)s, %(product_id)s, %(rating)s, %(rating_outof)s, %(author)s, %(country)s, %(reviewer_group)s, %(room_type)s, %(stay_detail)s, %(url)s, %(data_provider_id)s, %(product_name)s)")
        
        data_review = {
          'title': item['title'][0],
          'text': item['text'][0],
          'detect_lang': item['detect_lang'][0],
          'published_date_1': item['published_date_1'][0],
          'published_date': item['published_date'][0],
          'product_id': item['product_id'][0],
          'rating': item['rating'][0],
          'rating_outof': item['rating_outof'][0],
          'author': item['author'][0],
          'country': item['country'][0],
          'reviewer_group': item['reviewer_group'][0],
          'room_type': item['room_type'][0],
          'stay_detail': item['stay_detail'][0],
          'url': item['url'][0],
          'data_provider_id': item['data_provider_id'][0],
          'product_name': item['product_name'][0],
        }
        try:
            self.cursor.execute(add_review, data_review)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print('Re-encoding for error: %s' %err)
            text = item['text'][0].encode('utf-8')
            text_result = ''
            for t in text:
                if t in string.printable:
                    text_result += t

            title = item['title'][0].encode('utf-8')
            title_result = ''
            for t1 in title:
                if t1 in string.printable:
                    title_result += t1
            data_review = {
          'title': title_result,
          'text': text_result,
          'detect_lang': item['detect_lang'][0],
          'published_date_1': item['published_date_1'][0],
          'published_date': item['published_date'][0],
          'product_id': item['product_id'][0],
          'rating': item['rating'][0],
          'rating_outof': item['rating_outof'][0],
          'author': item['author'][0],
          'country': item['country'][0],
          'reviewer_group': item['reviewer_group'][0],
          'room_type': item['room_type'][0],
          'stay_detail': item['stay_detail'][0],
          'url': item['url'][0],
          'data_provider_id': item['data_provider_id'][0],
          'product_name': item['product_name'][0],
            }
            try:
                self.cursor.execute(add_review, data_review)
                self.cnx.commit()
            except mysql.connector.Error as err:
                print("Can't re-encode for error: %s" %err)
            else:
                print("Insert Review OK !!!")
        else:
            print("Insert Review OK !!!")

    def update_hotel(self, hotelId, lastDateCrawl):
        upd_hotel = ("UPDATE hotel SET last_date_crawl = '%s' WHERE hotel_id = %s" %(lastDateCrawl, hotelId))
        print(upd_hotel)
        try:
            self.cursor.execute(upd_hotel)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print(err)
        else:
            print("OK")
    def query_hotel(self):
        query_hotel = ("SELECT * FROM hotel")
        try:
            self.cursor.execute(query_hotel)
        except mysql.connector.Error as err:
            print(err)
        list = self.cursor
        return list
    def query_hotel_id(self):
        self.selectDB()
        query_hotel = ("SELECT hotel_id FROM hotel")
        try:
            self.cursor.execute(query_hotel)
        except mysql.connector.Error as err:
            print(err)
        list = self.cursor
        return list
    def close(self):
        self.cursor.close()
        self.cnx.close()
        print('closed ....')

if __name__ == '__main__':
    ins = connectMySQL()
    ins.create_database()
    ins.create_table()
    ins.insert_hotel(123, 'test Hotel', 'http://jasdklfjklsadfjlsadjlkf.com', date(2017, 2, 12))
    ins.update_hotel(123,date(2010, 10, 10))
    list = ins.query_hotel('123')
    for i in list:
        print(i)
    ins.close()

