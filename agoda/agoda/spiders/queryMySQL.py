import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta


class connectMySQL:
    DB_NAME = 'agoda'
    TABLES = {}
    TABLES['review'] = (
        "CREATE TABLE IF NOT EXISTS `review` ("
        "  `rev_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `title` varchar(255) ,"
        "  `text` text,"
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

    def create_table(self):
        try:
            self.cursor.execute(
                "USE {}".format(self.DB_NAME))
        except mysql.connector.Error as err:
            print(err)
            exit(1)
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
            print("OK")

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
    def query_hotel(self, hotelId):
        query_hotel = ("SELECT * FROM hotel WHERE hotel_id = %s" %hotelId)
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

