import re

from weverse.enums import NotificationType

from .community import PartialCommunity
from .member import PartialMember


class Notification:
    """Represents a Weverse Notification.

    .. container:: operations

        .. describe:: x == y

            Checks if two notifications are equal.

        .. describe:: x != y

            Checks if two notifications are not equal.

        .. describe:: hash(x)

            Returns the notification's hash.

        .. describe:: str(x)

            Returns the notification's message.

    Attributes
    ----------
    data: :class:`dict`
        The raw data directly taken from the response generated by Weverse's API.
    id: :class:`int`
        The ID of the notification.
    title: :class:`str`
        Usually the name of the group the notification belongs to.
        However, if it's an admin notification, it would be a proper title.
    message_ko: :class:`str`
        The message of the notification in Korean.
    message_ja: :class:`str`
        The message of the notification in Japanese.
    message_en: :class:`str`
        The message of the notification in English.
    image_url: :class:`str` | :class:`None`
        The URL to the image of the notification, if any.
    logo_image_url: :class:`str`
        The URL to the logo image of the notification.
    time_created: :class:`int`
        The time the notification got created at, in epoch.
    count: :class:`int`
        The number of artist comments on the post the notification
        leads to.
    is_read: :class:`bool`
        Whether the user has read the notification.
    community: :class:`.community.PartialCommunity`
        The :class:`.community.PartialCommunity` object of the community of
        the notification.
    author: :class:`.member.PartialMember` | :class:`None`
        The :class:`.member.PartialMember` object of the artist who
        created the post the notification leads to.

        Will always return :class:`None` for posts that are not
        comment-related.
    """

    __slots__ = (
        "data",
        "id",
        "title",
        "message_ko",
        "message_ja",
        "message_en",
        "image_url",
        "logo_image_url",
        "time_created",
        "count",
        "is_read",
        "community",
        "author",
    )

    def __init__(self, data: dict):
        self.data: dict = data
        self.id: int = data["activityId"]
        self.title: str = data["title"]
        self.message_ko: str = data["message"]["values"].get("ko", "")
        self.message_ja: str = data["message"]["values"].get("ja", "")
        self.message_en: str = data["message"]["values"].get("en", "")
        self.image_url: str | None = data.get("imageUrl")
        self.logo_image_url: str = data["logoImageUrl"]
        self.time_created: int = data["time"]
        self.count: int = data["count"]
        self.is_read: bool = data["read"]
        self.community: PartialCommunity = PartialCommunity(data["community"])
        self.author: PartialMember | None = (
            PartialMember(data["authors"][0]) if data.get("authors") else None
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id

        raise NotImplementedError

    def __repr__(self):
        return f"Notification notification_id={self.id}, message={self.message_en}"

    def __str__(self):
        return self.message_en

    def __hash__(self):
        return hash(self.id)

    @property
    def url(self) -> str:
        """:class:`str`: Returns the URL of the Weverse Post the Weverse
        Notification leads to."""
        return f"https://weverse.io{self.data['webUrl']}"

    @property
    def post_id(self) -> str:
        """:class:`str`: Returns the post ID of the post the notification leads to."""
        pattern = re.compile(r"([\d]-\d+)")
        match = re.search(pattern, self.data["messageId"])

        if not match:  # This happens when the notification type is Notice.
            match = re.search(r"\d+", self.data["messageId"])

        return match.group(0)

    @property
    def post_type(self) -> str:
        """:class:`str`: Returns the post type of the post the notification
        leads to.
        """
        post_types = {
            "T_FEED_COMMENT": NotificationType.USER_POST_COMMENT,
            "ST_FEED_COMMENT": NotificationType.USER_POST_COMMENT,
            "_MEDIA_COMMENT": NotificationType.MEDIA_COMMENT,
            "_MOMENT_COMMENT": NotificationType.MOMENT_COMMENT,
            "MOMENT_COMMENT": NotificationType.MOMENT_COMMENT,
            "ARTIST_COMMENT": NotificationType.ARTIST_POST_COMMENT,
            "ARTIST_POST": NotificationType.POST,
            "ARTIST_MOMENT": NotificationType.MOMENT,
            "ARTIST_LIVE_ON_AIR": NotificationType.LIVE,
            "COMMUNITY_MEDIA": NotificationType.MEDIA,
            "NOTICE": NotificationType.NOTICE,
            "COMMUNITY_ANNIVERSARY": NotificationType.BIRTHDAY,
        }

        for key, value in post_types.items():
            if key in self.data["messageId"]:
                return value

        return "NOT IMPLEMENTED"
