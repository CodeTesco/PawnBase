import re
from scrapy import Request, Spider, FormRequest
from form2request import form2request
from pawnSpider.items import TourneyItem
from scrapy_playwright.page import PageMethod

class TourneySpider(Spider):
    name = "tourneySpider"
    allowed_domains = ["s1.chess-results.com"]
    start_id = 1483442
    stop_id = 1483452
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

    def start_requests(self):
        yield from self._requests()

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
            tournament_id = response.xpath("//td[text()='FIDE-Event-ID']/following-sibling::td/a/text()").extract_first()
            tourney_name = response.css("h2::text").get()
            date = response.xpath("//td[@class='CR' and text()='Date']/following-sibling::td/text()").get()
            time_control = response.xpath("//td[@class='CR' and contains(text(), 'Time control')]/following-sibling::td/text()").get()
            time_control = time_control[:10] if time_control else None
            print(f"Tourney Name: {tourney_name}")
            print(f"Tournament ID: {tournament_id}")
            print(f"TC: {time_control}\n")
            yield TourneyItem(
                tournament_id=tournament_id,
                tourney_name=tourney_name,
                date=date,
                time_control=time_control,
            )
        except Exception as e:
            print(f"Second: {e}")