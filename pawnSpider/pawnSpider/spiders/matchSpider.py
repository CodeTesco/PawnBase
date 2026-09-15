from scrapy import Spider, Request
import psycopg2
import re
from pawnSpider.items import MatchItem

class matchSpider(Spider):
    name="matchSpider"

    def _requests(self):
        conn = psycopg2.connect(
            host="localhost",
            database="pawnbase",
            port="5432",
            user="postgres",
            password="codetesco"
        )
        cursor = conn.cursor()

        try:
            cursor.execute("select tournament_id from tournaments")
            tournament_id = cursor.fetchall()

            for (t_id,) in tournament_id:
                url = f"https://s1.chess-results.com/tnr{t_id}.aspx?lan=1&art=2&rd=1&turdet=YES&flag=30&SNode=S0"
                yield Request(url, callback=self.parse_items, cb_kwargs={"t_id": t_id, "round": 1})
        finally:
            cursor.close()
            conn.close()

    async def start(self):
        for request in self._requests():
            yield request

    def parse_items(self, response, t_id, round):
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
            white_id = None
            black_id = None

            try:
                conn = psycopg2.connect(
                    database="pawnbase",
                    user="postgres",
                    password="codetesco",
                    host="localhost",
                    port="5432"
                )
                cursor = conn.cursor()

                white_query = f"select player_id from players where name = '{white}'"
                black_query = f"select player_id from players where name = '{black}'"
                cursor.execute(white_query)
                white_id = cursor.fetchone()
                white_id = white_id[0] if white_id else None
                cursor.execute(black_query)
                black_id = cursor.fetchone()
                black_id = black_id[0] if black_id else None

            finally:
                cursor.close()
                conn.close()

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


        next_url = f"https://s1.chess-results.com/tnr{t_id}.aspx?lan=1&art=2&rd={round+1}&turdet=YES&flag=30&SNode=S0"
        yield Request(url=next_url, callback=self.parse_items, cb_kwargs={"t_id": t_id, "round": (round+1)})



