# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 去除前后空格
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != "description":
                value = adapter.get(field_name)
                adapter[field_name] = value[0].strip()

        # 统一内容为小写
        lowercase_keys = ["category", "product_type"]
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # 去掉价格里的英镑符号,并从字符串转成数字格式
        price_keys = ["price", "price_excl_tax", "price_incl_tax", "tax"]
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace("£", "")
            adapter[price_key] = float(value)

        # 若库存数量里有非必要的描述,仅保留库存数字(若无描述则库存为0),并转为整数格式
        availability_string = adapter.get("availability")
        split_string_array = availability_string.split("(")
        if len(split_string_array) < 0:
            adapter["availability"] = 0
        else:
            availability_array = split_string_array[1].split(" ")
            adapter["availability"] = int(availability_array[0])

        # 将评论数量从字符串转为整数格式
        num_reviews_string = adapter.get("num_reviews")
        adapter["num_reviews"] = int(num_reviews_string)

        # 将评分数量转化为整数格式
        stars_string = adapter.get("stars")
        split_stars_array = stars_string.split(" ")
        stars_text_value = split_stars_array[1].lower()
        STAR_MAP = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        adapter["stars"] = STAR_MAP.get(stars_text_value, -1)

        return item


import mysql.connector


class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="mysql", database="books"
        )

        self.cur = self.conn.cursor()

        self.cur.execute(
            """
CREATE TABLE
  IF NOT EXISTS books (
    id INT NOT NULL AUTO_INCREMENT,
    url VARCHAR(255),
    title TEXT,
    upc VARCHAR(255),
    product_type VARCHAR(255),
    price_excl_tax DECIMAL(10, 2),
    price_incl_tax DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    availability INT,
    num_reviews INT,
    stars INT,
    category VARCHAR(255),
    description TEXT,
    PRIMARY KEY (id)
  );
            """
        )

    def process_item(self, item, spider):
        self.cur.execute(
            """
        INSERT INTO
        books (
            url,
            title,
            upc,
            product_type,
            price_excl_tax,
            price_incl_tax,
            tax,
            availability,
            num_reviews,
            stars,
            category,
            description
        ) values(
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )          
                    """,
            (
                item["url"],
                item["title"],
                item["upc"],
                item["product_type"],
                item["price_excl_tax"],
                item["price_incl_tax"],
                item["tax"],
                item["availability"],
                item["num_reviews"],
                item["stars"],
                item["category"],
                str(item.get("description", [""])[0]),
            ),
        )
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
