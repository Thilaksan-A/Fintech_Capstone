from unittest.mock import ANY, MagicMock, patch
from app.services.sentiment.youtube.youtube_client import (
    build_youtube_client,
    search_youtube_videos,
    get_video_comments,
)
from app.schemas.youtube_schema import YoutubeVideoInfo, YoutubeCommentInfo


@patch("app.services.sentiment.youtube.youtube_client.build")
def test_build_youtube_client_success(mock_build):
    fake_resource = MagicMock()
    mock_build.return_value = fake_resource

    client = build_youtube_client()
    assert client is fake_resource
    mock_build.assert_called_once_with(
        "youtube",
        "v3",
        developerKey=ANY,
    )


@patch("app.services.sentiment.youtube.youtube_client.build")
def test_build_youtube_client_failure(mock_build, caplog):
    mock_build.side_effect = Exception("API error")
    with caplog.at_level("ERROR"):
        client = build_youtube_client()
        assert client is None
        assert "YouTube client could not be created" in caplog.text


@patch(
    "app.services.sentiment.youtube.youtube_client.parse_youtube_video_info",
)
def test_search_youtube_videos_yields_results(mock_parse):
    # Setup mock YouTube resource and response
    mock_youtube = MagicMock()
    mock_search = mock_youtube.search.return_value
    mock_list = mock_search.list.return_value
    mock_list.execute.return_value = {
        "items": [{"id": "vid1"}, {"id": "vid2"}],
        "nextPageToken": None,
    }
    # parse_youtube_video_info returns a YoutubeVideoInfo for each item
    mock_parse.side_effect = lambda item: YoutubeVideoInfo(
        video_id=item["id"],
        title="title",
        published_at="2025-07-28T12:00:00Z",
        etag="etag",
        description="description",
        channel="channel",
        channel_id="channelId",
    )
    results = list(
        search_youtube_videos(mock_youtube, "bitcoin", max_results=2),
    )
    assert len(results) == 2
    assert all(isinstance(r, YoutubeVideoInfo) for r in results)
    assert results[0].video_id == "vid1"
    assert results[1].video_id == "vid2"


@patch(
    "app.services.sentiment.youtube.youtube_client.parse_youtube_video_info",
)
def test_search_youtube_videos_handles_exception(mock_parse):
    mock_youtube = MagicMock()
    mock_search = mock_youtube.search.return_value
    mock_list = mock_search.list.return_value
    mock_list.execute.side_effect = Exception("API error")
    # Should not raise, should return nothing
    results = list(
        search_youtube_videos(mock_youtube, "bitcoin", max_results=2),
    )
    assert results == []


@patch(
    "app.services.sentiment.youtube.youtube_client.parse_youtube_comment_info",
)
def test_get_video_comments_yields_results(mock_parse):
    mock_youtube = MagicMock()
    mock_comment_threads = mock_youtube.commentThreads.return_value
    mock_list = mock_comment_threads.list.return_value
    mock_list.execute.return_value = {
        "items": [{"id": "c1"}, {"id": "c2"}],
        "nextPageToken": None,
    }
    # parse_youtube_comment_info returns a YoutubeCommentInfo for each item
    mock_parse.side_effect = lambda item: YoutubeCommentInfo(
        comment_id=item["id"],
        video_id="vid",
        text="comment",
        author="author",
        published_at="2025-07-28T12:00:00Z",
        updated_at="2025-07-28T12:01:00Z",
        reply_count=0,
        like_count=0,
        channel_id="chan",
        author_channel_id="authorChan",
        bot_score=0.0,
        crypto_mentions=[],
        raw_response=item,
    )
    results = list(get_video_comments(mock_youtube, "vid", max_results=2))
    assert len(results) == 2
    assert all(isinstance(r, YoutubeCommentInfo) for r in results)
    assert results[0].comment_id == "c1"
    assert results[1].comment_id == "c2"


@patch(
    "app.services.sentiment.youtube.youtube_client.parse_youtube_comment_info",
)
def test_get_video_comments_handles_exception(mock_parse):
    mock_youtube = MagicMock()
    mock_comment_threads = mock_youtube.commentThreads.return_value
    mock_list = mock_comment_threads.list.return_value
    mock_list.execute.side_effect = Exception("API error")
    results = list(get_video_comments(mock_youtube, "vid", max_results=2))
    assert results == []
