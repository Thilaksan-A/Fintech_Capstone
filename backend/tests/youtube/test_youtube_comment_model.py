from datetime import datetime
from app.models.youtube import YoutubeComment
from tests.factories.youtube import YoutubeCommentFactory


def test_youtube_comment_model(session):
    YoutubeCommentFactory(
        comment_id="test_comment",
        video_title="Test Video",
        text_original="This is a test comment.",
        like_count=10,
        total_reply_count=2,
        published_at=datetime.now(),
        updated_at=datetime.now(),
        raw_response={"key": "value"},
    )

    queried_comment = (
        session.query(YoutubeComment)
        .filter_by(comment_id="test_comment")
        .first()
    )

    assert queried_comment is not None
    assert queried_comment.video_id == "test_video"
    assert queried_comment.video_title == "Test Video"
    assert queried_comment.text_original == "This is a test comment."
    assert queried_comment.like_count == 10
    assert queried_comment.total_reply_count == 2
    assert queried_comment.raw_response == {"key": "value"}
