from scrapy import Spider, Request
import psycopg2
import re
from pawnSpider.items import MatchItem
from pawnSpider.config import DATABASE_CONFIG

class matchSpider(Spider):
    name="matchSpider"

    def _requests(self):
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("select tournament_id from tournaments")
        tournament_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT name, player_id FROM players")
        name_to_id = {name: player_id for name, player_id in cursor.fetchall()}
        cursor.close()
        conn.close()

        for t_id in tournament_ids[2000:]:
            url = f"https://s1.chess-results.com/tnr{t_id}.aspx?lan=1&art=2&rd=1&turdet=YES&flag=30&SNode=S0"
            yield Request(url, callback=self.parse_items, cb_kwargs={"t_id": t_id, "round": 1, "name_to_id": name_to_id})

    async def start(self):
        for request in self._requests():
            yield request

    def parse_items(self, response, t_id, round, name_to_id):
        if round > 3:
            return
        table = response.xpath("//table[contains(@class, 'CRs1')][1]")
        if not table:
            self.logger.info(f"Tournament {t_id} finished at round {round - 1}")
            return

        headers = table.xpath(".//tr[th]/th | .//tr[th]/td")
        col_map = {}
        current = ""

        for index, col in enumerate(headers):
            col_name = "".join(col.xpath(".//text()").getall()).strip().lower().replace(" ", "")
            if col_name:
                if col_name == "white":
                    current = "white"
                elif col_name == "black":
                    current = "black"
                if current == "white" and col_name in ["rtg", "rtgi", "rating"]:
                    col_name = "white_rating"
                elif current == "black" and col_name in ["rtg", "rtgi", "rating"]:
                    col_name = "black_rating"
                col_map[col_name] = index

        player_rows = table.xpath(".//tr[td]")
        players = player_rows[1:]

        if "team" in col_map:
            return
        print(col_map)
        print(t_id)

        for index, player in enumerate(players):
            cells = player.xpath("./td")

            def get_cell_data(possible_names):
                for target in possible_names:
                    for key, index in col_map.items():
                        if target in key and index < len(cells):
                            text = "".join(cells[index].xpath(".//text()").getall()).strip()
                            return text if text else None
                return None

            white = get_cell_data(["white"])
            black = get_cell_data(["black"])

            white_rtg = get_cell_data(["white_rating"])
            white_rtg = int(white_rtg) if white_rtg else None

            black_rtg = get_cell_data(["black_rating"])
            black_rtg = int(black_rtg) if black_rtg else None

            result = get_cell_data(["result"])

            white_id = name_to_id.get(white)
            black_id = name_to_id.get(black)

            match_id = f"{t_id}_R{round}_B{index+1}"
            # print(match_id)
            # print(white)
            # print(white_id)
            # print(black)
            # print(black_id)
            # print(result)
            # print("")

            yield MatchItem(
                match_id=match_id,
                tournament_id=t_id,
                white_id=white_id,
                black_id=black_id,
                result=result,
                white_rtg=white_rtg,
                black_rtg=black_rtg
            )

            # stopped at 2000


        next_url = f"https://s1.chess-results.com/tnr{t_id}.aspx?lan=1&art=2&rd={round+1}&turdet=YES&flag=30&SNode=S0"
        yield Request(url=next_url, callback=self.parse_items, cb_kwargs={"t_id": t_id, "round": (round+1), "name_to_id": name_to_id})



