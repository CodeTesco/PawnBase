import re
from scrapy import Request, Spider, FormRequest
from pawnSpider.items import TourneyItem
from .utils import clean_date, clean_tc
# from form2request import form2request

class TourneySpider(Spider):
    name = "tourneySpider"
    allowed_domains = ["s1.chess-results.com"]
    start_id = 1350000
    stop_id = 1353000
    # start_urls = [f"https://s1.chess-results.com/tnr{start_id}.aspx?lan=1&flag=30&turdet=YES&SNode=S0"]

    def _requests(self):
        for id in range(self.start_id, self.stop_id):
            try:
                url = f"https://s1.chess-results.com/tnr{id}.aspx?lan=1&flag=30&turdet=YES&SNode=S0"
                yield Request(url=url, callback=self.parse)
            except Exception as e:
                print(f"First: {e}")

    async def start(self):
        for request in self._requests():
            yield request

    # def start_requests(self):
    #     yield from self._requests()

    def parse(self, response):
        gate_button = response.css("input#cb_alleDetails")
        
        if gate_button:
            yield FormRequest.from_response(
                response,
                clickdata={"id": "cb_alleDetails"},
                callback=self.parse_data
            )
        else:
            yield from self.parse_data(response)

    def parse_data(self, response):
        try: 
            # tournament_id = response.xpath("//td[text()='FIDE-Event-ID']/following-sibling::td/a/text()").get()
            tournament_match = re.search(r"/tnr(\d+)\.aspx", response.url)
            tournament_id = tournament_match.group(1) if tournament_match else None

            tourney_name = response.css("h2::text").get()
            date = response.xpath("//td[@class='CR' and text()='Date']/following-sibling::td/text()").get()
            time_control = response.xpath("//td[@class='CR' and contains(text(), 'Time control')]/following-sibling::td/text()").get()
            base_mins, inc_sec = clean_tc(time_control)
            date = clean_date(date)
            location = response.xpath("//td[text()='Location']/following-sibling::td/a/text()").get()

            print(f"Tourney Name: {tourney_name}")
            print(f"Tournament ID: {tournament_id}")
            # print(f"TC: {base_mins}mins + {inc_sec}secs")
            # print(f"Date: {date}\n")

            yield TourneyItem(
                tournament_id=tournament_id,
                tourney_name=tourney_name,
                date=date,
                location=location,
                base_minutes=base_mins,
                increment_seconds=inc_sec
            )
        except Exception as e:
            print(f"Second: {e}")