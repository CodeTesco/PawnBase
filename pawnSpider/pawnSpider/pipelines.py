# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
from pawnSpider.items import TourneyItem, PlayerItem

class PawnspiderPipeline:
    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host="localhost",
            database="pawnbase",
            user="postgres",
            password="codetesco",
            port="5432"
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, TourneyItem):
            insert_query = """
                insert into tournaments (tournament_id, tourney_name, date, base_minutes, increment_seconds) values (%s, %s, %s, %s, %s)
                on conflict (tournament_id) do nothing
            """
            try:
                self.cursor.execute(insert_query, (
                    item.get("tournament_id"),
                    item.get("tourney_name"),
                    item.get("date"),
                    item.get("base_minutes"),
                    item.get("increment_seconds")
                ))
                self.connection.commit()
            except psycopg2.Error as e:
                spider.logger.error(f"Database Error: {e}")
                self.connection.rollback()
        else:
            pass

        return item


