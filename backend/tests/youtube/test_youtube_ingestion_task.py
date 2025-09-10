from unittest.mock import patch, MagicMock
from app.services.sentiment.youtube import (
    collect_youtube_crypto_comments,
)


@patch("app.services.sentiment.youtube._store_comments_and_analysis")
@patch("app.services.sentiment.youtube.sanitise_comments")
@patch("app.services.sentiment.youtube.get_video_comments")
@patch("app.services.sentiment.youtube.search_youtube_videos")
@patch("app.services.sentiment.youtube.build_youtube_client")
def test_execute_youtube_ingestion_task(
    mock_build_client,
    mock_search_videos,
    mock_get_comments,
    mock_sanitise_comments,
    mock_store_comments,
    subtests,
):
    # Setup mocks
    mock_client = MagicMock()
    mock_build_client.return_value = mock_client

    # Simulate video found
    video_info = MagicMock()
    video_info.video_id = "vid1"
    video_info.title = "Test Video"
    mock_search_videos.return_value = [video_info]

    # Simulate comments found
    comment = MagicMock()
    comment.comment_id = "c1"
    comment.video_id = "vid1"
    comment.text = "BTC to the moon!"
    comment.like_count = 1
    comment.reply_count = 0
    comment.published_at = "2025-07-28T12:00:00Z"
    comment.updated_at = "2025-07-28T12:01:00Z"
    comment.raw_response = {"id": "c1"}
    comment.crypto_mentions = ["BTC"]
    mock_get_comments.return_value = [comment]

    # Simulate sanitise_comments returns the comment
    mock_sanitise_comments.return_value = [comment]

    # Run the task
    collect_youtube_crypto_comments(
        video_query="bitcoin",
        max_videos_search=1,
        max_comments_search=1,
        ranking=10,
    )

    # Check that the client was built
    mock_build_client.assert_called_once()
    # Check that videos were searched
    mock_search_videos.assert_called_once_with(
        mock_client,
        query="bitcoin",
        max_results=1,
    )
    # Check that comments were fetched
    mock_get_comments.assert_called_once_with(
        mock_client,
        video_id="vid1",
        max_results=1,
    )
    # Check that sanitise_comments was called
    mock_sanitise_comments.assert_called_once_with([comment], 10)
    # Check that store function was called
    mock_store_comments.assert_called_once_with([comment], video_info)


@patch("app.services.sentiment.youtube.build_youtube_client")
def test_execute_youtube_ingestion_task_no_client(mock_build_client):
    mock_build_client.return_value = None
    # Should return early, nothing else called
    collect_youtube_crypto_comments("bitcoin", 1, 1, 10)
    mock_build_client.assert_called_once()


@patch("app.services.sentiment.youtube.build_youtube_client")
@patch("app.services.sentiment.youtube.search_youtube_videos")
def test_execute_youtube_ingestion_task_no_videos(
    mock_search_videos,
    mock_build_client,
):
    mock_build_client.return_value = MagicMock()
    mock_search_videos.return_value = []
    collect_youtube_crypto_comments("bitcoin", 1, 1, 10)
    mock_search_videos.assert_called_once()


@patch("app.services.sentiment.youtube.build_youtube_client")
@patch("app.services.sentiment.youtube.search_youtube_videos")
@patch("app.services.sentiment.youtube.get_video_comments")
def test_execute_youtube_ingestion_task_no_comments(
    mock_get_comments,
    mock_search_videos,
    mock_build_client,
):
    mock_build_client.return_value = MagicMock()
    video_info = MagicMock()
    video_info.video_id = "vid1"
    video_info.title = "Test Video"
    mock_search_videos.return_value = [video_info]
    mock_get_comments.return_value = []
    collect_youtube_crypto_comments("bitcoin", 1, 1, 10)
    mock_get_comments.assert_called_once()


@patch("app.services.sentiment.youtube.build_youtube_client")
@patch("app.services.sentiment.youtube.search_youtube_videos")
@patch("app.services.sentiment.youtube.get_video_comments")
@patch("app.services.sentiment.youtube.sanitise_comments")
def test_execute_youtube_ingestion_task_no_filtered_comments(
    mock_sanitise_comments,
    mock_get_comments,
    mock_search_videos,
    mock_build_client,
):
    mock_build_client.return_value = MagicMock()
    video_info = MagicMock()
    video_info.video_id = "vid1"
    video_info.title = "Test Video"
    mock_search_videos.return_value = [video_info]
    mock_get_comments.return_value = [MagicMock()]
    mock_sanitise_comments.return_value = []
    collect_youtube_crypto_comments("bitcoin", 1, 1, 10)
    mock_sanitise_comments.assert_called_once()


# Add tests for the store function
@patch("app.services.sentiment.youtube.db")
@patch("app.services.sentiment.youtube.insert")
@patch("app.services.sentiment.youtube.select")
def test_store_comments_and_analysis_new_comments(
    mock_select,
    mock_insert,
    mock_db,
):
    from app.services.sentiment.youtube import _store_comments_and_analysis

    # Setup mocks
    mock_db.session.scalars.return_value.all.return_value = (
        []
    )  # No existing comments
    mock_insert_stmt = MagicMock()
    mock_insert.return_value = mock_insert_stmt
    mock_insert_stmt.on_conflict_do_nothing.return_value = mock_insert_stmt

    # Create mock video info
    video_info = MagicMock()
    video_info.title = "Test Video"

    # Create mock comments
    comment = MagicMock()
    comment.comment_id = "c1"
    comment.video_id = "vid1"
    comment.text = "BTC to the moon!"
    comment.like_count = 1
    comment.reply_count = 0
    comment.published_at = "2025-07-28T12:00:00Z"
    comment.updated_at = "2025-07-28T12:01:00Z"
    comment.raw_response = {"id": "c1"}
    comment.crypto_mentions = ["BTC"]

    # Call the function
    _store_comments_and_analysis([comment], video_info)

    # Verify database operations
    assert (
        mock_db.session.execute.call_count == 2
    )  # One for comments, one for analysis
    mock_insert.assert_called()


@patch("app.services.sentiment.youtube.db")
@patch("app.services.sentiment.youtube.select")
def test_store_comments_and_analysis_existing_comments(
    mock_select,
    mock_db,
):
    from app.services.sentiment.youtube import _store_comments_and_analysis

    # Setup mocks - existing comment found
    mock_db.session.scalars.return_value.all.return_value = ["c1"]

    # Create mock video info
    video_info = MagicMock()
    video_info.title = "Test Video"

    # Create mock comments
    comment = MagicMock()
    comment.comment_id = "c1"
    comment.crypto_mentions = ["BTC"]

    # Call the function
    _store_comments_and_analysis([comment], video_info)

    # Verify no inserts happened (comment already exists)
    mock_db.session.execute.assert_not_called()


def test_store_comments_and_analysis_empty_list():
    from app.services.sentiment.youtube import _store_comments_and_analysis

    video_info = MagicMock()

    # Should return early for empty list
    result = _store_comments_and_analysis([], video_info)
    assert result is None
