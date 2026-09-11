from scrapy import Spider, Request
import psycopg2
from pawnSpider.items import PlayerItem

class PlayerSpider(Spider):
    name="playerSpider"

    def _requests(self):
        connection = psycopg2.connect(
            database="pawnbase",
            user="postgres",
            host="localhost",
            password="codetesco",
            port="5432"
        )
        cursor = connection.cursor()
        query = "select tournament_id, base_minutes from tournaments"
        cursor.execute(query)
        tournament_id = cursor.fetchall()

        for id, tc_mins in [(1467473, 60)]:
            if int(id) >= 1000000:
                url = f"https://s3.chess-results.com/tnr{id}.aspx?lan=1"
                yield Request(url=url, callback=self.parse_items, meta={"tc_mins": tc_mins})
            else:
                continue

    async def start(self):
        for request in self._requests():
            yield request

    def parse_items(self, response, tc_mins):
        rows = response.xpath("//h2[contains(text(), 'Starting rank')]/following-sibling::table//tr")
        players = rows[1:]
        for player in players:
            row = []
            for td in player.xpath("./td"):
                cell = td.xpath("string(.)").get(default="").strip()
                row.append(cell)
            player_id = row[3]
            name = row[2]
            title = row[1]
            standard_rating = None
            rapid_rating = None
            blitz_rating = None

            if tc_mins == None:
                rapid_rating = row[5]
            if tc_mins >= 60:
                standard_rating = row[5]
            elif tc_mins < 60 and tc_mins > 10:
                rapid_rating = row[5]
            else:
                blitz_rating = row[5]
            gender = "Male" if row[6].strip() == "" else "Female"

            yield PlayerItem(
                player_id=player_id,
                name=name,
                title=title,
                standard_rating=standard_rating,
                blitz_rating=blitz_rating,
                gender=gender,
                rapid_rating=rapid_rating
            )


    # player_id | name | title | standard_rating | blitz_rating | gender | rapid_rating