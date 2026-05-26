# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock

from agency import telegram

@pytest.fixture(autouse=True)
def configure_telegram(mocker):
    # Set fake token and chat ID for testing
    mocker.patch.object(telegram, "TELEGRAM_TOKEN", "fake_token")
    mocker.patch.object(telegram, "TELEGRAM_CHAT_ID", "123456789")
    mocker.patch.object(telegram, "TELEGRAM_API", "https://api.telegram.org/botfake_token")
    mocker.patch.object(telegram, "AUTHORIZED_USER_ID", 123456789)

def test_send_post_success(mocker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post = mocker.patch("requests.post", return_value=mock_response)
    
    res = telegram.send_post(1, "INSIDER TRUTH", "AI Topic", "Post content")
    assert res is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "chat_id" in kwargs["json"]
    assert "Post content" in kwargs["json"]["text"]

def test_send_approval_buttons(mocker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post = mocker.patch("requests.post", return_value=mock_response)
    
    res = telegram.send_approval_buttons("AI Topic", 4)
    assert res is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "reply_markup" in kwargs["json"]
    assert len(kwargs["json"]["reply_markup"]["inline_keyboard"]) == 5  # 4 posts + 1 reject all

def test_wait_for_approval_authorized(mocker):
    # Mock requests.get for polling
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 100,
                "callback_query": {
                    "id": "query_id_123",
                    "from": {"id": 123456789},  # Authorized
                    "data": "publish_2"
                }
            }
        ]
    }
    mocker.patch("requests.get", return_value=mock_get_response)
    
    # Mock requests.post for responses
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post = mocker.patch("requests.post", return_value=mock_post_response)
    
    res = telegram.wait_for_approval(timeout_minutes=1)
    assert res == 2
    assert mock_post.call_count == 2  # 1 for answerCallbackQuery, 1 for confirmation message

def test_wait_for_approval_unauthorized(mocker):
    # Mock requests.get with unauthorized user
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 100,
                "callback_query": {
                    "id": "query_id_123",
                    "from": {"id": 999999999},  # Unauthorized
                    "data": "publish_2"
                }
            }
        ]
    }
    mocker.patch("requests.get", return_value=mock_get_response)
    
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post = mocker.patch("requests.post", return_value=mock_post_response)
    
    # Mock sleep to break loop or timeout quickly
    mocker.patch("time.time", side_effect=[0, 10, 100]) # runs once then timeouts
    
    res = telegram.wait_for_approval(timeout_minutes=1)
    assert res is None
    # Verify that answerCallbackQuery denied access
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "Access denied" in kwargs["json"]["text"]
