import scrapy
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        "FEEDS": {"booksdata.json": {"format": "json", "overwrite": True}},
    }

    def parse(self, response):
        """
        Parse the main book list page to extract book URLs and navigate pagination.

        This method processes the response received from the start URLs. It extracts
        individual book URLs from the current page and initiates a request to parse
        each book's detailed information using the parse_book_page method. Additionally,
        it handles pagination by identifying the next page link and recursively calling
        itself to continue scraping subsequent pages.

        Args:
        response (scrapy.http.Response): The response object from the start URL or
        the current page being processed.
        """

        books = response.css("article.product_pod")
        # 依次打开本页之书，并爬取数据
        for book in books:
            relative_url = book.css("h3 a").attrib["href"]
            if "catalogue/" in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        # 切换到下一页，递归执行自身
        next_page = response.css("li.next a ::attr(href)").get()
        if next_page is not None:
            if "catalogue/" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        """
        This function is used to parse the information of a single book page.

        This function takes a response object as parameter and returns a dictionary
        containing the information of the book. The information includes the title,
        upc, product type, prices, tax, availability, number of reviews, stars,
        category, description and price of the book.
        """

        book = response.css("div.product_main")[0]
        book_item = BookItem()
        table_rows = response.css("table tr")  # 取出来就是数组,后面慢慢筛选

        book_item["url"] = (response.url,)
        book_item["title"] = (book.css("h1 ::text").get(),)
        book_item["upc"] = (table_rows[0].css("td ::text").get(),)
        book_item["product_type"] = (table_rows[1].css("td ::text").get(),)
        book_item["price_excl_tax"] = (table_rows[2].css("td ::text").get(),)
        book_item["price_incl_tax"] = (table_rows[3].css("td ::text").get(),)
        book_item["tax"] = (table_rows[4].css("td ::text").get(),)
        book_item["availability"] = (table_rows[5].css("td ::text").get(),)
        book_item["num_reviews"] = (table_rows[6].css("td ::text").get(),)
        book_item["stars"] = (book.css("p.star-rating").attrib["class"],)
        book_item["category"] = (
            book.xpath(
                "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()"
            ).get(),
        )
        book_item["description"] = (
            book.xpath(
                "//div[@id='product_description']/following-sibling::p/text()"
            ).get(),
        )
        book_item["price"] = (book.css("p.price_color ::text").get(),)

        yield book_item


# scrapy crawl bookspider -O parsed_booksdata.json