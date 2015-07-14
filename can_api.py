#-*- coding: utf-8 -*-

import endpoints
import feedparser
import re

from datetime import datetime
from models import Feed
from models import FeedItem
from models import FeedItemImage
from models import GroupResult
from models import GroupResultList
from models import Match
from models import MatchResult
from models import MatchResultList
from models import Team
from models import Result
from models import Score
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from time import mktime


CAN_GROUP_A_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-a-c951.xml'
CAN_GROUP_B_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-b-c954.xml'
CAN_GROUP_C_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-c-c952.xml'
CAN_GROUP_D_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-groupe-d-c953.xml'
CAN_QUARTER_FINAL_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-' \
                                  'des-nations-quart-de-finale-c950.xml'
CAN_SEMI_FINAL_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-demi-finale-c966.xml'
CAN_THIRD_PLACE_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-3eme-place-c949.xml'
CAN_FINAL_FEED_URL = 'http://www.matchendirect.fr/rss/foot-can-coupe-afrique-des-nations-finale-c762.xml'
CAN_YEAR = 2015


def is_rss_feed_valid(rss):
    if not type(rss) is feedparser.FeedParserDict:
        raise TypeError('Wrong type for parameter \'rss\': expected <class \'feedparser.FeedParserDict\'> '
                        'but found %s:' % type(rss))
    is_valid = True
    is_valid = is_valid and ('channel' in rss)
    is_valid = is_valid and ('title' in rss['channel'])
    is_valid = is_valid and ('link' in rss['channel'])
    is_valid = is_valid and ('description' in rss['channel'])
    is_valid = is_valid and ('image' in rss['channel'])
    is_valid = is_valid and ('url' in rss['channel']['image'])
    is_valid = is_valid and ('title' in rss['channel']['image'])
    is_valid = is_valid and ('link' in rss['channel']['image'])
    is_valid = is_valid and ('width' in rss['channel']['image'])
    is_valid = is_valid and ('height' in rss['channel']['image'])
    is_valid = is_valid and ('items' in rss)
    is_valid = is_valid and (type(rss['items']) is list)
    is_valid = is_valid and len(rss['items']) > 0
    if is_valid:
        for item in rss['items']:
            is_valid = is_valid and ('title' in item)
            is_valid = is_valid and ('link' in item)
            is_valid = is_valid and ('guid' in item)
            is_valid = is_valid and ('published_parsed' in item)
    return is_valid


def get_rss_feed_parser(url):
    rss = feedparser.parse(url)
    return rss


def get_feed_from_url(url):
    """
    Download a rss 2.0 feed and returns a class which represents that feed.
    :param url: URL of the feed to download.
    :return: Feed
    """
    rss = get_rss_feed_parser(url)
    if not is_rss_feed_valid(rss):
        raise LookupError('Sorry! We cannot parse the rss feed. Missing required element(s).')
    feed = Feed()
    feed.title = rss['channel']['title']
    feed.link = rss['channel']['link']
    feed.description = rss['channel']['description']
    feed.image = FeedItemImage(url=rss['channel']['image']['url'],
                               title=rss['channel']['image']['title'],
                               link=rss['channel']['image']['link'],
                               width=rss['channel']['image']['width'],
                               height=rss['channel']['image']['height'])
    feed.items = []
    for item in rss['items']:
        feed.items.append(FeedItem(title=item['title'], link=item['link'],
                                   guid=item['guid'],
                                   pub_date=datetime.fromtimestamp(mktime(item['published_parsed']))))
    return feed


def get_matches_from_feed(feed, level, number_of_matches=6):
    """
    Returns collection of matches
    :param feed: Feed from which matches will be retrieved.
    :param level: Level of the tournament
    :param number_of_matches: Number of matches to retrieve
    :return: Collection of matches
    """
    regex_score = '\(score final : \d+-\d+\)'
    start_index = 0
    titles_with_score = [item.title for item in feed.items if re.search(regex_score, item.title)
                         and item.pub_date.year == CAN_YEAR][start_index:number_of_matches]
    team_bloc = 1
    score_bloc = 2
    counter = 0
    matches = dict()
    for title in titles_with_score:
        # Example of title 'Championnat National U-19 : Saint-Lô Manche U19 - Quevilly U19 (score final : 0-3)'
        title_blocs = title.encode('utf-8').split(':', 2)
        # Now title_blocs is an array of size three (3):
        # 'Championnat National U-19 '
        # and
        # ' Saint-Lô Manche U19 - Quevilly U19 (score final '
        # and
        # ' 0-3)'
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


def get_results_from_matches(matches):
    """
    Returns the results (points, etc.) computed with data
    in the feed.
    :param matches: Collection of matches
    :return: Collection of matches
    """
    if not type(matches) is dict:
        raise TypeError('Wrong type for parameter \'matches\': expected <type \'dict\'> but found %s:' % type(matches))
    teams = dict()
    results = dict()
    # Get all teams
    for match in matches.values():
        if match.teams[0].name not in teams:
            teams[match.teams[0].name] = match.teams[0]
        if match.teams[1].name not in teams:
            teams[match.teams[1].name] = match.teams[1]
    # Initialize results
    for team in teams.values():
        results[team.name] = Result(team=team, pts=0, goal_for=0, goal_against=0, goal_diff=0)
    # Computes results (points, goal for, goal against, etc) for each match.
    for match in matches.values():
        results[match.teams[0].name].goal_for += match.scores[0].value
        results[match.teams[0].name].goal_against += match.scores[1].value
        results[match.teams[1].name].goal_for += match.scores[1].value
        results[match.teams[1].name].goal_against += match.scores[0].value
        if match.scores[0].value > match.scores[1].value:
            results[match.teams[0].name].pts += 3
        elif match.scores[0].value < match.scores[1].value:
            results[match.teams[1].name].pts += 3
        else:
            results[match.teams[0].name].pts += 1
            results[match.teams[1].name].pts += 1
    for key in results.keys():
        results[key].goal_diff = results[key].goal_for - results[key].goal_against

    return results


def get_feed_group(group_letter):
    """
    Download feed for the group with the given letter in upper case
    :param group_letter: Letter of the group
    :return: Feed for group
    """
    try:
        if group_letter == 'A':
            feed_group = get_feed_from_url(CAN_GROUP_A_FEED_URL)
        elif group_letter == 'B':
            feed_group = get_feed_from_url(CAN_GROUP_B_FEED_URL)
        elif group_letter == 'C':
            feed_group = get_feed_from_url(CAN_GROUP_C_FEED_URL)
        elif group_letter == 'D':
            feed_group = get_feed_from_url(CAN_GROUP_D_FEED_URL)
        else:
            return None
    except LookupError:
        return None

    return feed_group


def get_group_results(upper_letter):
    """
    Returns the results for the group with the given letter in upper case.
    :param upper_letter: Letter of the group.
    :return: Result for the group
    """
    feed_group = get_feed_group(upper_letter)

    if not feed_group:
        return GroupResult(group_name='Groupe {0}'.format(upper_letter), results=[])

    matches = get_matches_from_feed(feed_group, 'Phase de groupe')
    result = get_results_from_matches(matches)
    result_group = GroupResult(group_name='Groupe {0}'.format(upper_letter),
                               results=[result for result in result.values()])
    return result_group


def get_group_matches(group_letter):
    """
    Returns the matches for the group with the given letter.
    :param group_letter: Letter of the group
    :return: Collection of matches
    """
    feed_group = get_feed_group(group_letter)

    if not feed_group:
        return MatchResult(matches=[], group_name='Groupe {0}'.format(group_letter))

    matches = get_matches_from_feed(feed_group, 'Phase de groupe')
    return MatchResult(matches=[match for match in matches.values()],
                       group_name='Groupe {0}'.format(group_letter))


def get_matches(feed_url, tournament_level_name, number_of_matches):
    try:
        feed_group = get_feed_from_url(feed_url)
    except LookupError:
        feed_group = None

    if not feed_group:
        return None

    matches = get_matches_from_feed(feed_group, tournament_level_name, number_of_matches=number_of_matches)
    return matches


@endpoints.api(name='can', version='v1', description='CAN 2015 API')
class CanApi(remote.Service):
    GROUP_NAME_RESOURCE_CONTAINER = endpoints.ResourceContainer(
        message_types.VoidMessage,
        upper_letter=messages.StringField(1, variant=messages.Variant.STRING))

    @endpoints.method(message_types.VoidMessage, GroupResultList,
                      path='results/group/all', http_method='GET', name='results.groups.all')
    def results_groups_all(self, request):
        """
        Returns the results for all groups of the tournament.
        :param request: Request handler
        :return: Collection of results.
        """
        results_group_a = get_group_results('A')
        results_group_b = get_group_results('B')
        results_group_c = get_group_results('C')
        results_group_d = get_group_results('D')
        return GroupResultList(group_results=[results_group_a, results_group_b, results_group_c, results_group_d])

    @endpoints.method(message_types.VoidMessage, MatchResultList,
                      path='matches/group/all', http_method='GET', name='matches.groups.all')
    def matches_groups_all(self, request):
        """
        Returns all the matches for all groups of the tournament.
        :param request: Request handler
        :return: Collection of matches
        """
        matches_group_a = get_group_matches('A')
        matches_group_b = get_group_matches('B')
        matches_group_c = get_group_matches('C')
        matches_group_d = get_group_matches('D')
        return MatchResultList(matches_results=[matches_group_a, matches_group_b, matches_group_c, matches_group_d])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/quarter/final', http_method='GET', name='matches.quarter.final')
    def matches_quarter_final(self, request):
        """
        Returns the matches for quarter final
        :param request: request handler
        :return: collection of matches.
        """
        matches = get_matches(CAN_QUARTER_FINAL_FEED_URL, 'Quarts de finale', number_of_matches=4)

        if not matches:
            return MatchResult(matches=[],)

        return MatchResult(matches=[match for match in matches.values()])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/semi/final', http_method='GET', name='matches.semi.final')
    def matches_semi_final(self, request):
        """
        Returns the matches for semi final
        :param request: request handler
        :return: collection of matches.
        """
        matches = get_matches(CAN_SEMI_FINAL_FEED_URL, 'Demi-finales', number_of_matches=2)

        if not matches:
            return MatchResult(matches=[],)

        return MatchResult(matches=[match for match in matches.values()])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/third/place', http_method='GET', name='matches.third.place')
    def matches_third_place(self, request):
        """
        Returns the match for third place
        :param request: request handler
        :return: collection of matches.
        """
        matches = get_matches(CAN_THIRD_PLACE_FEED_URL, 'Match pour la 3ème place', number_of_matches=1)

        if not matches:
            return MatchResult(matches=[],)

        return MatchResult(matches=[match for match in matches.values()])

    @endpoints.method(message_types.VoidMessage, MatchResult,
                      path='matches/final', http_method='GET', name='matches.final')
    def matches_final(self, request):
        """
        Returns the match for the final
        :param request: request handler
        :return: collection of matches.
        """
        matches = get_matches(CAN_FINAL_FEED_URL, 'Finale', number_of_matches=1)

        if not matches:
            return MatchResult(matches=[],)

        return MatchResult(matches=[match for match in matches.values()])

APPLICATION = endpoints.api_server([CanApi], restricted=False)