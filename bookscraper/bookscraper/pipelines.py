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