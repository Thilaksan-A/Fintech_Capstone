from datetime import datetime
import factory
from app.models.youtube import YoutubeComment, YoutubeCommentAnalysis
from tests.factories import BaseFactory
from tests.factories.crypto import CryptoAssetFactory

mock_raw_response = {
    "kind": "youtube#commentThreadListResponse",
    "etag": "xxxxxxxxxxxx",
    "pageInfo": {"totalResults": 1, "resultsPerPage": 100},
    "items": [
        {
            "kind": "youtube#commentThread",
            "etag": "xxxxxxxxxxx",
            "id": "xxxxxxxxxxxx",
            "snippet": {
                "channelId": "xxxxxxxxxx",
                "videoId": "xxxxxxxx",
                "topLevelComment": {
                    "kind": "youtube#comment",
                    "etag": "xxxxxxxxxxxxx",
                    "id": "xxxxxxxxxxxx",
                    "snippet": {
                        "channelId": "xxxxxxxxxx",
                        "videoId": "xxxxxxxxxx",
                        "textDisplay": "This is a test comment.",
                        "textOriginal": "This is a test comment.",
                        "authorDisplayName": "@mock_user",
                        "authorProfileImageUrl": "https://yt3.ggpht.com/ytc/xxxxxxxxx",
                        "authorChannelUrl": "http://www.youtube.com/@mock_user",
                        "authorChannelId": {"value": "xxxxxxxxxx"},
                        "canRate": True,
                        "viewerRating": "none",
                        "likeCount": 0,
                        "publishedAt": "2025-06-16T09:41:10Z",
                        "updatedAt": "2025-06-16T09:41:10Z",
                    },
                },
                "canReply": True,
                "totalReplyCount": 0,
                "isPublic": True,
            },
        },
    ],
}


class YoutubeCommentFactory(BaseFactory):
    class Meta:
        model = YoutubeComment

    comment_id = "test_comment"
    video_id = "test_video"
    video_title = "Test Video"
    text_original = "This is a test comment."
    like_count = 100
    total_reply_count = 3
    published_at = datetime(2025, 1, 1).astimezone()
    updated_at = datetime(2025, 1, 1).astimezone()
    raw_response = mock_raw_response

    # Use RelatedFactoryList for one-to-many
    analysis = factory.RelatedFactoryList(
        "tests.factories.youtube.YoutubeCommentAnalysisFactory",
        factory_related_name="comment",
        size=0,
    )


class YoutubeCommentAnalysisFactory(BaseFactory):
    class Meta:
        model = YoutubeCommentAnalysis

    comment = factory.SubFactory(YoutubeCommentFactory)
    comment_id = factory.SelfAttribute("comment.comment_id")
    crypto_symbol = factory.SelfAttribute("crypto_asset.symbol")
    confidence_score = 0.75
    relevance_score = 0.85
    quality_score = 0.95
    analysed_at = datetime(2025, 1, 1).astimezone()
    crypto_asset = factory.SubFactory(CryptoAssetFactory)
