from scrapy import Spider, Request
import psycopg2
from pawnSpider.items import PlayerItem
from pawnSpider.config import DATABASE_CONFIG

class PlayerSpider(Spider):
    name="playerSpider"

    def _requests(self):
        connection = psycopg2.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()
        try:
            query = "select tournament_id, base_minutes from tournaments"
            cursor.execute(query)
            tournament_details = cursor.fetchall()

            for id, tc_mins in tournament_details[100:]:
                if int(id) >= 1000000:
                    url = f"https://s1.chess-results.com/tnr{id}.aspx?lan=1"
                    yield Request(url=url, callback=self.parse_items, cb_kwargs={"tc_mins": tc_mins})
        finally:
            cursor.close()
            connection.close()

    async def start(self):
        for request in self._requests():
            yield request

    VALID_TITLES = {"GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"}

    def parse_items(self, response, tc_mins):
        candidate_tables = []
        for table in response.xpath("//table"):
            headers = table.xpath("./tr[th]/th")
            header_text = " ".join(headers.xpath(".//text()").getall()).lower()
            if "fideid" in header_text and table.xpath("./tr[td][1]/td"):
                candidate_tables.append(table)

        table = max(
            candidate_tables,
            key=lambda candidate: len(candidate.xpath("./tr[td][1]/td")),
            default=None,
        )
        if not table:
            title = response.xpath("string(//title)").get(default="").strip()
            self.logger.warning(
                "No player table: url=%s status=%s length=%s title=%r",
                response.url,
                response.status,
                len(response.body),
                title,
            )
            return

        headers = table.xpath("./tr[th]/th")
        col_map = {}

        for index, col in enumerate(headers):
            col_name = "".join(col.xpath(".//text()").getall()).lower().strip().replace(" ", "")
            if col_name:
                col_map[col_name] = index

        if "team" in col_map:
            return
        print(col_map)

        players = table.xpath("./tr[td]")
        for player in players:
            cells = player.xpath("./td")

            def get_cell_data(possible_names):
                for target in possible_names:
                    for key, index in col_map.items():
                        if target in key and index < len(cells):
                            text = "".join(cells[index].xpath(".//text()").getall()).strip()
                            return text if text else None
                return None

            name = get_cell_data(["name"])
            player_id = get_cell_data(["fideid", "fide-id"])
            if not player_id or not player_id.isdigit():
                continue

            title = None
            for cell in cells:
                cell_text = "".join(cell.xpath(".//text()").getall()).strip().upper()
                if cell_text in self.VALID_TITLES:
                    title = cell_text
                    break

            rating_text = get_cell_data(["rtg", "rtgi", "rating"])
            rating_digit = int(rating_text) if rating_text and rating_text.isdigit() else None

            standard_rating = None
            rapid_rating = None
            blitz_rating = None

            if tc_mins is None:
                rapid_rating = rating_digit
            elif tc_mins >= 60:
                standard_rating = rating_digit
            elif tc_mins < 60 and tc_mins > 10:
                rapid_rating = rating_digit
            else:
                blitz_rating = rating_digit

            gender_text = get_cell_data(["sex", "gender"])
            gender = "Female" if gender_text else "Male"

            yield PlayerItem(
                player_id=player_id,
                name=name,
                title=title,
                standard_rating=standard_rating,
                blitz_rating=blitz_rating,
                gender=gender,
                rapid_rating=rapid_rating
            )