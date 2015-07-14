#-*- coding: utf-8 -*-

from protorpc import messages
from protorpc import message_types


class Team(messages.Message):
    """
    Represents a team in the competition.
    """
    name = messages.StringField(1)
    abbr = messages.StringField(2)


class Score(messages.Message):
    """
    Score for a match.
    """
    value = messages.IntegerField(1)


class Group(messages.Message):
    """
    Represents a group in the tournament.
    """
    name = messages.StringField(1)
    teams = messages.MessageField(Team, 2, repeated=True)


class Result(messages.Message):
    team = messages.MessageField(Team, 1)
    pts = messages.IntegerField(2)
    goal_for = messages.IntegerField(3)
    goal_against = messages.IntegerField(4)
    goal_diff = messages.IntegerField(5)


class GroupResult(messages.Message):
    """
    Holds the results for the group.
    """
    group_name = messages.StringField(1)
    results = messages.MessageField(Result, 2, repeated=True)


class GroupResultList(messages.Message):
    """
    Collection of results for all groups.
    """
    group_results = messages.MessageField(GroupResult, 1, repeated=True)


class Match(messages.Message):
    """
    Represents a match in the tournament.
    """
    guid = messages.StringField(1)
    level = messages.StringField(2)
    details_link = messages.StringField(3)
    teams = messages.MessageField(Team, 4, repeated=True)
    scores = messages.MessageField(Score, 5, repeated=True)


class MatchResult(messages.Message):
    """
    Represents all matches for a specific group.
    """
    group_name = messages.StringField(1)
    matches = messages.MessageField(Match, 2, repeated=True)


class MatchResultList(messages.Message):
    """
    Represents all matches of the tournament.
    """
    matches_results = messages.MessageField(MatchResult, 1, repeated=True)


class FeedItemImage(messages.Message):
    """
    Holds details of an Image in a feed.

    see: http://cyber.law.harvard.edu/rss/rss.html
    """
    url = messages.StringField(1)
    title = messages.StringField(2)
    link = messages.StringField(3)
    width = messages.IntegerField(4)
    height = messages.IntegerField(5)


class FeedItem(messages.Message):
    """
    Represents an Item in a RSS feed.

    see: http://cyber.law.harvard.edu/rss/rss.html
    """
    title = messages.StringField(1)
    link = messages.StringField(2)
    guid = messages.StringField(3)
    pub_date = message_types.DateTimeField(4)


class Feed(messages.Message):
    """
    Represents the root of the RSS feed.

    see: http://cyber.law.harvard.edu/rss/rss.html
    """
    title = messages.StringField(1)
    link = messages.StringField(2)
    description = messages.StringField(3)
    image = messages.MessageField(FeedItemImage, 4)
    items = messages.MessageField(FeedItem, 5, repeated=True)
    updated_date = message_types.DateTimeField(6)