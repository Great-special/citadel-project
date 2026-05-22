import json
from datetime import date
from django.db.models import Prefetch, Q

from .models import Category, Cluster, Course, UpcomingEvent

DEFAULT_FEE = '€3,999'


def serialize_tracks():
    """
    Returns a Python list shaped exactly like DEFAULT_TRACKS in the JS.

    Key contract:
      - track['id']   = array index (0, 1, 2 …) — NOT the DB PK.
                        The JS switchTrackById() treats this as an array index.
      - course['id']  = str(course.pk) — string so the JS onclick('id') strict-equals work.
      - cluster['id'] = cluster.slug (e.g. 'aim') — matches JS currentCluster comparison.
      - Synthetic 'all' cluster prepended automatically if the track has any clusters.
    """
    categories = Category.objects.prefetch_related(
        Prefetch('clusters', queryset=Cluster.objects.order_by('order', 'id')),
        Prefetch(
            'courses',
            queryset=Course.objects.select_related('cluster').order_by('rank_id', 'id')
        ),
    ).order_by('order', 'id')[:5]

    tracks = []
    for idx, cat in enumerate(categories):
        clusters = list(cat.clusters.all())
        courses  = list(cat.courses.all())

        track = {
            'id':      idx,          # array index — keeps switchTrackById() correct
            'label':   cat.name,
            'short':   cat.short or cat.name,
            'color':   cat.color or '#C8960C',
            'faculty': cat.faculty,
            'bespoke': cat.bespoke,
        }
        if cat.badge:
            track['badge'] = cat.badge

        if clusters:
            track['clusters'] = [
                {'id': 'all', 'label': 'All Programmes', 'color': cat.color or '#C8960C'},
            ] + [
                {
                    'id':    cl.slug,
                    'label': cl.label,
                    'color': cl.color or cat.color or '#C8960C',
                }
                for cl in clusters
            ]

        track['courses'] = [
            {
                'id':       str(c.pk),
                'num':      c.num,
                'title':    c.title,
                'subtitle': c.subtitle,
                'duration': c.duration,
                'level':    c.level,
                'teaser':   c.teaser,
                'synopsis': c.description,   # description field = synopsis content
                'audience': c.audience,
                'fee':      f'€{int(c.price):,}' if c.price else DEFAULT_FEE,
                'cluster':  c.cluster.slug if c.cluster_id else None,
            }
            for c in courses
        ]

        tracks.append(track)

    return tracks


def serialize_upcoming():
    """
    Returns a Python list shaped exactly like DEFAULT_UPCOMING in the JS.
    Only returns events that have not yet expired.
    """
    today = date.today()
    events = UpcomingEvent.objects.filter(
        Q(expires__isnull=True) | Q(expires__gte=today)
    )

    result = []
    for e in events:
        item = {
            'id':       e.slug,
            'title':    e.title,
            'subtitle': e.subtitle,
            'partners': e.partners,
            'dates':    e.dates,
            'location': e.location,
            'expires':  e.expires.isoformat() if e.expires else None,
            'sectors':  e.sectors or [],
            'stats':    e.stats or [],
            'body':     e.body,
        }
        if e.facilitator_name:
            item['facilitator'] = {
                'label': e.facilitator_label or 'Lead Facilitator',
                'name':  e.facilitator_name,
                'bio':   e.facilitator_bio,
            }
        result.append(item)

    return result