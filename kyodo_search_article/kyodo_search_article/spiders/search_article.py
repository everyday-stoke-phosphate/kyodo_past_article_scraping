# -*- coding: utf-8 -*-
import json
import urllib.parse

import scrapy


class SearchArticleSpider(scrapy.Spider):
    name = 'search_article'
    allowed_domains = ['cms.nordot.jp', 'this.kiji.is']

    # start_urls = [
    #     "https://cms.nordot.jp/cu/sources/getListPost?"
    #     "query=unit_id%3A39166665832988672+"
    #     "created_at%3A%3E%3D2020-03-01T00%3A00%3A00%2B09%3A00+"
    #     "created_at%3A%3C%3D2020-03-02T00%3A00%3A00%2B09%3A00"
    #     "&offset=0"
    #     "&limit=100"
    #     ]

    def __init__(self, *args, **kwargs):
        super(SearchArticleSpider, self).__init__(*args, **kwargs)
        # 初期変数を作成
        self.page_offset = 0
        self.page_limit = 100
        # 複数の保存するファイルを用意

    def start_requests(self):
        # 目的のjsonのURLを生成する

        # # urllib用のパラメータ
        url = self.make_next_url()
        yield scrapy.Request(url)

    def make_next_url(self, offset=None, limit=None):
        # 目的のjsonのURLを返す関数
        if offset is None:
            offset = self.page_offset
        if limit is None:
            limit = self.page_limit
        query_words = "unit_id:39166665832988672 " \
                      "created_at:>=2020-01-01T00:00:00+09:00 " \
                      "created_at:<=2020-01-08T00:00:00+09:00"  # todo 検索する期間の日付とunit idを外部から渡せるように変更
        query = urllib.parse.urlencode({"query": query_words, "offset": offset, "limit": limit})

        # urlunparseに渡すデータ作成(リストもしくはタプルで　辞書は壊れる)
        # パラメータまとめると見にくいので分割
        SCHEME: str = 'https'
        NETLOC: str = 'cms.nordot.jp'
        PATH: str = '/cu/sources/getListPost'
        FRAGMENT = None
        PARAMS = None
        # urlunparseに渡す順番を変えると壊れるので順番は変えないこと
        url_data: list = [SCHEME, NETLOC, PATH, FRAGMENT, query, PARAMS]
        return urllib.parse.urlunparse(url_data)

    def parse(self, response):
        # jsonに関するコード
        json_response = json.loads(response.body_as_unicode())

        # 全てのデータを格納する
        for data in json_response["data"]["posts"]:  # todo ["data"]["posts"]などは変数化
            yield {
                "url": data["url"],
                "title": data["title"],
                "subtitle": data["subtitle"],
                "description": data["description"],
                "published_at": data["published_at"]
            }

        # todo キーワードに引っかかったものを別ファイルに保存

        # todo キーワードに引っかからなかった記事で記事の本文をスクレイピング

        # 次のjsonが存在するかチェックして存在したら取得
        if json_response["data"]["paging"]["has_next"]:
            print("次===========================")
            self.page_offset = self.page_offset + self.page_limit
            yield scrapy.Request(
                self.make_next_url(
                    offset=self.page_offset,
                    limit=self.page_limit
                ),
                callback=self.parse
            )

        pass

    def parse_article_detail(self):
        # todo 記事の詳細をパース

        # 記事に指定のワードが含まれているものを保存

        # 記事に指定のワードが含まれて```いない```ものを保存

        pass
