#-*- coding: utf-8 -*-
__author__ = 'OUATTARA Gninlikpoho Romuald'

import endpoints
import feedparser
import logging
import re

from datetime import datetime
from time import mktime

from protorpc import messages
from protorpc import message_types
from protorpc import remote


CAN_2015_GROUP_A_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-a-c951.xml'
CAN_2015_GROUP_B_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-b-c954.xml'
CAN_2015_GROUP_C_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-c-c952.xml'
CAN_2015_GROUP_D_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-d-c953.xml'
CAN_2015_QUARTER_FINAL_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-' \
                                  'des-nations-quart-de-finale-c950.xml'
CAN_2015_SEMI_FINAL_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-demi-finale-c966.xml'
CAN_2015_THIRD_PLACE_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-3eme-place-c949.xml'
CAN_2015_FINAL_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-finale-c762.xml'


class Team(messages.Message):
    name = messages.StringField(1)
    abbr = messages.StringField(2)


class Score(messages.Message):
    value = messages.IntegerField(1)


class Group(messages.Message):
    name = messages.StringField(1)
    teams = messages.MessageField(Team, 2, repeated=True)


class Result(messages.Message):
    team = messages.MessageField(Team, 1)
    pts = messages.IntegerField(2)
    bp = messages.IntegerField(3)  # But pour
    bc = messages.IntegerField(4)  # But contre
    db = messages.IntegerField(5)  # Difference de but


class GroupResult(messages.Message):
    group_name = messages.StringField(1)
    results = messages.MessageField(Result, 2, repeated=True)


class GroupResultList(messages.Message):
    group_results = messages.MessageField(GroupResult, 1, repeated=True)


class Match(messages.Message):
    guid = messages.StringField(1)
    level = messages.StringField(2)
    details_link = messages.StringField(3)
    teams = messages.MessageField(Team, 4, repeated=True)
    scores = messages.MessageField(Score, 5, repeated=True)


class MatchResult(messages.Message):
    group_name = messages.StringField(1)
    matches = messages.MessageField(Match, 2, repeated=True)


class MatchResultList(messages.Message):
    matches_results = messages.MessageField(MatchResult, 1, repeated=True)


class FeedItemImage(messages.Message):
    url = messages.StringField(1)
    title = messages.StringField(2)
    link = messages.StringField(3)
    width = messages.IntegerField(4)
    height = messages.IntegerField(5)


class FeedItem(messages.Message):
    title = messages.StringField(1)
    link = messages.StringField(2)
    guid = messages.StringField(3)
    pub_date = message_types.DateTimeField(4)


class Feed(messages.Message):
    title = messages.StringField(1)
    link = messages.StringField(2)
    description = messages.StringField(3)
    image = messages.MessageField(FeedItemImage, 4)
    items = messages.MessageField(FeedItem, 5, repeated=True)
    updated_date = message_types.DateTimeField(6)


def get_feed_from_url(url):
    """
    Returns feed from url
    :param url: URL of the feed
    :return: Feed
    """
    f = feedparser.parse(url)
    feed = Feed()
    feed.title = f['channel']['title']
    feed.link = f['channel']['link']
    feed.description = f['channel']['description']
    feed.image = FeedItemImage(url=f['channel']['image']['url'],
                               title=f['channel']['image']['title'],
                               link=f['channel']['image']['link'],
                               width=f['channel']['image']['width'],
                               height=f['channel']['image']['height'])
    feed.items = []
    for item in f['items']:
        feed.items.append(FeedItem(title=item['title'], link=item['link'],
                                   guid=item['guid'],
                                   pub_date=datetime.fromtimestamp(mktime(item['published_parsed']))))
    return feed


def get_matches_from_feed(feed, level, start_index=0, end_index=6):
    """
    Returns collection of matches
    :param feed: Feed from which matches will be retrieved.
    :param level: Level of the competition
    :param start_index: Start index
    :param end_index: End index
    :return: Collection of matches
    """
    regex_score = '\(score final : \d+-\d+\)'
    titles_with_score = [item.title for item in feed.items if re.search(regex_score, item.title) and
                        item.pub_date.year==2015][start_index:end_index]
    logging.error('TITLE WITH SCORES: %s' % (titles_with_score,))
    team_bloc = 1
    score_bloc = 2
    counter = 0
    matches = dict()
    for title in titles_with_score:
        title_blocs = title.encode('utf-8').split(':', 2)

        team_a_name = title_blocs[team_bloc].split(' - ', 1)[0].strip()
        team_b_name = title_blocs[team_bloc].split(' - ', 1)[1].replace(' (score final ', '').strip()
        team_a_score = title_blocs[score_bloc].split('-', 1)[0].strip()
        team_b_score = title_blocs[score_bloc].split('-', 1)[1].replace(')', '').strip()
        # Team creation
        team_a = Team(name=team_a_name.decode('utf-8'), abbr=None)
        team_b = Team(name=team_b_name.decode('utf-8'), abbr=None)
        # Match creation
        current_item = feed.items[counter]
        match = Match(guid=current_item.guid, details_link=current_item.link,
                      level=level.decode('utf-8'), scores=[Score(value=int(team_a_score)),
                                                           Score(value=int(team_b_score))],
                      teams=[team_a, team_b])
        matches[str(match.guid)] = match
        counter += 1
    return matches


def get_results_from_matches(matches=dict()):
    """
    Returns the results (points, etc.) computed with data
    in the feed.
    :param matches: Collection of matches
    :return: Collection of matches
    """
    teams = dict()
    results = dict()
    for match in matches.values():
        if match.teams[0].name not in teams:
            teams[match.teams[0].name] = match.teams[0]
        if match.teams[1].name not in teams:
            teams[match.teams[1].name] = match.teams[1]
    for team in teams.values():
        results[team.name] = Result(team=team, pts=0, bp=0, bc=0, db=0)
    for match in matches.values():
        results[match.teams[0].name].bp += match.scores[0].value
        results[match.teams[0].name].bc += match.scores[1].value
        results[match.teams[1].name].bp += match.scores[1].value
        results[match.teams[1].name].bc += match.scores[0].value
        if match.scores[0].value > match.scores[1].value:
            results[match.teams[0].name].pts += 3
        elif match.scores[0].value < match.scores[1].value:
            results[match.teams[1].name].pts += 3
        else:
            results[match.teams[0].name].pts += 1
            results[match.teams[1].name].pts += 1
    for key in results.keys():
        results[key].db = results[key].bp - results[key].bc

    return results


def get_feed_group(group_letter):
    """
    Download feed for the group with the given letter in upper case
    :param group_letter: Letter of the group
    :return: Feed for group
    """
    if group_letter == 'A':
        feed_group = get_feed_from_url(CAN_2015_GROUP_A_FEED_URL)
    elif group_letter == 'B':
        feed_group = get_feed_from_url(CAN_2015_GROUP_B_FEED_URL)
    elif group_letter == 'C':
        feed_group = get_feed_from_url(CAN_2015_GROUP_C_FEED_URL)
    elif group_letter == 'D':
        feed_group = get_feed_from_url(CAN_2015_GROUP_D_FEED_URL)
    else:
        return None

    return feed_group


def results_groups(upper_letter):
    """
    Returns the results for the group with the given letter in upper case.
    :param upper_letter: Letter of the group.
    :return: Result for the group
    """
    feed_group = get_feed_group(upper_letter)

    if not feed_group:
        return GroupResult(group_name='Groupe {0}'.format(upper_letter),
                           results=[])

    matches = get_matches_from_feed(feed_group, 'Phase de groupe')
    result = get_results_from_matches(matches)
    result_group = GroupResult(group_name='Groupe {0}'.format(upper_letter),
                               results=[result for result in result.values()])
    return result_group


def matches_groups(upper_letter):
    """
    Returns the matches for the group with the given letter.
    :param upper_letter: Letter of the group
    :return: Collection of matches
    """
    feed_group = get_feed_group(upper_letter)

    if not feed_group:
        return MatchResult(matches=[], group_name='Groupe {0}'.format(upper_letter))

    matches = get_matches_from_feed(feed_group, 'Phase de groupe')
    return MatchResult(matches=[match for match in matches.values()],
                       group_name='Groupe {0}'.format(upper_letter))


@endpoints.api(name='can', version='v1', description='CAN 2015 API')
class CanApi(remote.Service):
    GROUP_NAME_RESOURCE_CONTAINER = endpoints.ResourceContainer(
        message_types.VoidMessage,
        upper_letter=messages.StringField(1, variant=messages.Variant.STRING))

    @endpoints.method(message_types.VoidMessage, GroupResultList,
                      path='results/group/all', http_method='GET', name='results.group.all')
    def results_groups_all(self, request):
        """
        Returns a collection of results
        :param request: Request handler
        :return: Collection of results
        """
        results_groups_a = results_groups('A')
        results_groups_b = results_groups('B')
        results_groups_c = results_groups('C')
        results_groups_d = results_groups('D')
        return GroupResultList(group_results=[results_groups_a, results_groups_b,
                                              results_groups_c, results_groups_d])

    # Tous les matchs de la can

    @endpoints.method(message_types.VoidMessage, MatchResultList,
                      path='matches/group/all', http_method='GET', name='matches.groups.all')
    def matches_groups_all(self, request):
        """
        Returns all the matches for all groups of the competition
        :param request: Request handler
        :return: Collection of matches
        """
        matches_groups_a = matches_groups('A')
        matches_groups_b = matches_groups('B')
        matches_groups_c = matches_groups('C')
        matches_groups_d = matches_groups('D')
        return MatchResultList(matches_results=[matches_groups_a, matches_groups_b, matches_groups_c, matches_groups_d])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/quarter/final', http_method='GET', name='matches.quarter.final')
    def matches_quarter_final(self, request):
        """
        Returns the matches for quarter final
        :param request: request handler
        :return: collection of matches.
        """
        feed_group = get_feed_from_url(CAN_2015_QUARTER_FINAL_FEED_URL)

        if not feed_group:
            return MatchResult(matches=[],)

        matches = get_matches_from_feed(feed_group, 'Quarts de finale', start_index=0, end_index=4)
        return MatchResult(matches=[match for match in matches.values()])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/semi/final', http_method='GET', name='matches.semi.final')
    def matches_semi_final(self, request):
        """"
        Returns the matches for semi final
        :param request: request handler
        :return: collection of matches.
        """
        feed_group = get_feed_from_url(CAN_2015_SEMI_FINAL_FEED_URL)

        if not feed_group:
            return MatchResult(matches=[],)

        matches = get_matches_from_feed(feed_group, 'Demi-finales', start_index=0, end_index=2)
        return MatchResult(matches=[match for match in matches.values()])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/third/place', http_method='GET', name='matches.third.place')
    def matches_third_place(self, request):
        """
        Returns the matches for third place
        :param request: request handler
        :return: collection of matches.
        """
        feed_group = get_feed_from_url(CAN_2015_THIRD_PLACE_FEED_URL)

        if not feed_group:
            return MatchResult(matches=[],)

        matches = get_matches_from_feed(feed_group, 'Match pour la 3ème place', start_index=0, end_index=1)
        return MatchResult(matches=[match for match in matches.values()])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/final', http_method='GET', name='matches.final')
    def matches_final(self, request):
        """
        Returns the matches for final
        :param request: request handler
        :return: collection of matches.
        """
        feed_group = get_feed_from_url(CAN_2015_FINAL_FEED_URL)

        if not feed_group:
            return MatchResult(matches=[],)

        matches = get_matches_from_feed(feed_group, 'Finale', start_index=0, end_index=1)
        return MatchResult(matches=[match for match in matches.values()])

APPLICATION = endpoints.api_server([CanApi], restricted=False)