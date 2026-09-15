# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class PlayerItem(scrapy.Item):
    player_id = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    standard_rating = scrapy.Field()
    blitz_rating = scrapy.Field()
    gender = scrapy.Field()
    rapid_rating = scrapy.Field()
    
class TourneyItem(scrapy.Item):
    tournament_id = scrapy.Field()
    tourney_name = scrapy.Field()
    date = scrapy.Field()
    location = scrapy.Field()
    base_minutes = scrapy.Field()
    increment_seconds = scrapy.Field()

class MatchItem(scrapy.Item):
    match_id = scrapy.Field()
    tournament_id = scrapy.Field()
    white_id = scrapy.Field()
    black_id = scrapy.Field()
    result = scrapy.Field()
    white_rtg = scrapy.Field()
    black_rtg = scrapy.Field()

