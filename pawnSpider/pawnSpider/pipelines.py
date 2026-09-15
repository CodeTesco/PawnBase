# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
from pawnSpider.items import TourneyItem, PlayerItem, MatchItem

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
                insert into tournaments (tournament_id, tourney_name, date, location, base_minutes, increment_seconds) values (%s, %s, %s, %s, %s, %s)
                on conflict (tournament_id) do nothing
            """
            try:
                self.cursor.execute(insert_query, (
                    item.get("tournament_id"),
                    item.get("tourney_name"),
                    item.get("date"),
                    item.get("location"),
                    item.get("base_minutes"),
                    item.get("increment_seconds")
                ))
                self.connection.commit()
            except psycopg2.Error as e:
                spider.logger.error(f"Database Error: {e}")
                self.connection.rollback()
        elif isinstance(item, PlayerItem):
            insert_query = """
                insert into players (player_id, name, title, standard_rating, blitz_rating, gender, rapid_rating) values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (player_id)
                do update set
                name = excluded.name,
                title = coalesce(excluded.title, players.title),
                standard_rating = coalesce(excluded.standard_rating, players.standard_rating),
                blitz_rating = coalesce(excluded.blitz_rating, players.blitz_rating);
            """
            try:
                self.cursor.execute(insert_query, (
                    item.get("player_id"),
                    item.get("name"),
                    item.get("title"),
                    item.get("standard_rating"),
                    item.get("blitz_rating"),
                    item.get("gender"),
                    item.get("rapid_rating")
                ))
                self.connection.commit()
            except psycopg2.Error as e:
                spider.logger.error(f"Database Error; {e}")
                self.connection.rollback()
        elif isinstance(item, MatchItem):
            insert_query = """
                INSERT INTO matches (match_id, tournament_id, white_id,black_id, result, white_rtg, black_rtg)
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT DO NOTHING;
            """
            try:
                self.cursor.execute(insert_query, (
                    item.get("match_id"),
                    item.get("tournament_id"),
                    item.get("white_id"),
                    item.get("black_id"),
                    item.get("result"),
                    item.get("white_rtg"),
                    item.get("black_rtg")
                ))
                self.connection.commit()
            except psycopg2.Error as e:
                spider.logger.error(f"Database Error: {e}")
                self.connection.rollback()

        return item


