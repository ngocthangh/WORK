import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta
from agoda.items import AgodaReviewItem
import sys
import string
from agoda.spiders.ConfigurationManager import agodaConfig

class connectMySQL:
    TABLES = {}
    TABLES['review'] = (
        "CREATE TABLE IF NOT EXISTS `review` ("
        "  `rev_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `title` varchar(255) CHARACTER SET utf8,"
        "  `comment` text CHARACTER SET utf8,"
        "  `language` varchar(10),"
        "  `date_publish_timestamp` bigint(15),"
        "  `date_publish` date,"

        "  `product_id` int(11),"
        "  `review_score` float,"
        "  `rating_out_of` varchar(20),"
        "  `author` varchar(255),"
        "  `country` varchar(255),"

        "  `type_of_trip` varchar(255),"
        "  `room_type` varchar(255),"
        "  `details_stay` varchar(255),"
        "  `link` varchar(255),"
        # "  `data_provider_id` int(11),"
        "  `product_name` varchar(255),"
        "  `source_sentiment` varchar(50),"
        "  PRIMARY KEY (`rev_no`)"
        ") ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_general_ci")

    TABLES['city'] = (
        "CREATE TABLE IF NOT EXISTS `city` ("
        "  `city_id` varchar(15) NOT NULL,"
        "  `city_name` varchar(255),"
        "  `is_active` TINYINT(1),"
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
        self.Config = agodaConfig()
        self.DB_NAME = self.Config.DB_NAME
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
        for name, ddl in self.TABLES.items():
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
    def insert_city(self, cityId, cityName, isactive):
        add_city = ("INSERT INTO city "
              "(city_id, city_name, is_active) "
              "VALUES (%(city_id)s, %(city_name)s, %(isactive)s)")
        data_city = {
          'city_id': cityId,
          'city_name': cityName,
          'isactive' : isactive,
        }
        try:
            self.cursor.execute(add_city, data_city)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print(err)
        else:
            print("Insert City OK !!!")
    def update_city(self, cityId, isactive):
        upd_city = ("UPDATE city SET is_active = '%s' WHERE city_id = %s" %(isactive, cityId))
        try:
            self.cursor.execute(upd_city)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print(err)
        else:
            print("Update City OK")
    def insert_review(self, it):
        item = it.load_item()
        add_review = ("INSERT INTO review "
              "(title, comment, language, date_publish, date_publish_timestamp, product_id, review_score, rating_out_of, author, country, type_of_trip, room_type, details_stay, link, product_name, source_sentiment) "
              "VALUES (%(title)s, %(comment)s, %(language)s, %(date_publish)s, %(date_publish_timestamp)s, %(product_id)s, %(review_score)s, %(rating_out_of)s, %(author)s, %(country)s, %(type_of_trip)s, %(room_type)s, %(details_stay)s, %(link)s, %(product_name)s, %(source_sentiment)s)")
        
        data_review = {
          'title': item['title'][0],
          'comment': item['comment'][0],
          'language': item['language'][0],
          'date_publish': item['date_publish'][0],
          'date_publish_timestamp': item['date_publish_timestamp'][0],
          'product_id': item['product_id'][0],
          'review_score': item['review_score'][0],
          'rating_out_of': item['rating_out_of'][0],
          'author': item['author'][0],
          'country': item['country'][0],
          'type_of_trip': item['type_of_trip'][0],
          'room_type': item['room_type'][0],
          'details_stay': item['details_stay'][0],
          'link': item['link'][0],
          # 'data_provider_id': item['data_provider_id'][0],
          'product_name': item['product_name'][0],
          'source_sentiment': item['source_sentiment'][0],
            }
        try:
            self.cursor.execute(add_review, data_review)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print('Re-encoding for error: %s' %err)
            text = item['comment'][0].encode('utf-8')
            text_result = ''
            for t in text:
                if str(t) in string.printable:
                    text_result += str(t)

            title = item['title'][0].encode('utf-8')
            title_result = ''
            for t1 in title:
                if str(t1) in string.printable:
                    title_result += str(t1)
            data_review = {
          'title': title_result,
          'comment': text_result,
          'language': item['language'][0],
          'date_publish': item['date_publish'][0],
          'date_publish_timestamp': item['date_publish_timestamp'][0],
          'product_id': item['product_id'][0],
          'review_score': item['review_score'][0],
          'rating_out_of': item['rating_out_of'][0],
          'author': item['author'][0],
          'country': item['country'][0],
          'type_of_trip': item['type_of_trip'][0],
          'room_type': item['room_type'][0],
          'details_stay': item['details_stay'][0],
          'link': item['link'][0],
          # 'data_provider_id': item['data_provider_id'][0],
          'product_name': item['product_name'][0],
          'source_sentiment': item['source_sentiment'][0],
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

