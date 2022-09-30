from app.models import Feed
from app import db

from datetime import datetime
from pendulum import timezone


"""
Generalized functions for returning feed metrics

# TODO: Add docstrings for all functions
# TODO: Likely can refactor and further generalize logic  
"""


class UserMetrics:
    def return_most_recent_feed_time(self):
        return timezone("UTC").convert(
            db.session.query(db.func.max(Feed.feed_timestamp))
            .filter(Feed.child_id == self.active_child)
            .first()[0]
        )

    def return_min_since_last_feed(self):
        delta = self.most_recent_feed_time - timezone(self.user_tz).convert(
            self.user_current_time
        )
        return delta.total_seconds() / 60

    def return_current_day_feeds(self):
        user_current_time_utc = timezone("UTC").convert(self.user_current_time).date()
        return self.format_feed_list(
            Feed.query.filter(
                Feed.child_id == self.active_child,
                Feed.feed_timestamp >= user_current_time_utc,
            ).all()
        )

    def format_feed_list(self, feed_list):
        formatted_list = [
            {
                "feed_timestamp": self.prepare_display_date(
                    timezone("UTC").convert(feed.feed_timestamp)
                ),
                "feed_type": self.format_feed_type(feed.feed_type),
            }
            for feed in feed_list
        ]

        return formatted_list

    def format_feed_type(self, feed_type):
        if feed_type == "breast":
            return "Breast"
        elif feed_type == "bottle":
            return "Bottle"
        elif feed_type == "breast_plus_bottle":
            return "Breast + Bottle"

    # Assumes that duration is input as minutes
    def format_duration(self, duration):
        abs_duration = abs(duration)
        hrs = int(abs_duration / 60)
        if hrs > 0:
            duration_string = f"{hrs} Hours and {int(abs_duration % 60)} Minutes"
        else:
            duration_string = f"{int(abs_duration)} Minutes"
        return duration_string

    def prepare_display_date(self, dt):
        return self.format_date_string(self.convert_utc_to_user_tz(dt))

    def convert_utc_to_user_tz(self, dt):
        return timezone(self.user_tz).convert(dt)

    def format_date_string(self, dt):
        return dt.strftime(self.date_format)

    def __init__(self, user_active_child):
        # TODO: Replace hard-coded user_tz and date_format with dynamic variables
        #   import time
        #   time.tzname
        self.user_tz = "US/Eastern"
        self.date_format = "%Y-%m-%d %I:%M %p"
        self.user_current_time = datetime.now()
        self.active_child = user_active_child
        self.most_recent_feed_time = self.return_most_recent_feed_time()
        self.most_recent_feed_display_time = self.prepare_display_date(
            self.most_recent_feed_time
        )
        self.time_since_last_feed = self.format_duration(
            self.return_min_since_last_feed()
        )
        self.current_day_feeds = self.return_current_day_feeds()
