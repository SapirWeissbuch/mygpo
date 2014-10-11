from collections import Counter

from mygpo.podcasts.models import Episode
from mygpo.history.models import EpisodeHistoryEntry


def played_episode_counts(user):
    """ number of played episodes per podcast for the given user """
    # retrieve list of unique episodes that the user has played.
    # for each episode only it's podcast is returned, because we don't care
    # about which episodes exactly have been played, only the number
    podcasts = EpisodeHistoryEntry.objects\
                                  .filter(user=user,
                                          action=EpisodeHistoryEntry.PLAY)\
                                  .order_by('episode__id')\
                                  .distinct('episode__id')\
                                  .values_list('episode__podcast', flat=True)
    return Counter(podcasts)


def num_played_episodes(user, since=None, until=None):
    """ Number of distinct episodes the user has played in the interval """
    query = EpisodeHistoryEntry.objects\
                               .filter(user=user,
                                       action=EpisodeHistoryEntry.PLAY)\
                               .order_by('episode__id')\
                               .distinct('episode__id')

    if since is not None:
        query = query.filter(timestamp__gt=since)

    if until is not None:
        query = query.filter(timestamp__lte=until)

    return query.count()


def last_played_episodes(user, limit=10):
    """ The last episodes that the user played """
    ep_ids = EpisodeHistoryEntry.objects\
                                .filter(user=user,
                                        action=EpisodeHistoryEntry.PLAY)\
                                .order_by('episode__id', '-timestamp')\
                                .distinct('episode__id')\
                                .values_list('episode__id')
    ep_ids = ep_ids[:limit]
    episodes = Episode.objects.filter(id__in=ep_ids)\
                              .select_related('podcast')\
                              .prefetch_related('slugs',
                                                'podcast__slugs')
    return episodes
