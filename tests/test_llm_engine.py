# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, patch

from agency import llm_engine

@pytest.fixture(autouse=True)
def reset_errors():
    # Reset error tracking before each test
    llm_engine._provider_errors = {"openrouter": 0, "deepseek": 0, "gemini": 0}

def test_call_llm_success_openrouter(mocker):
    # Mock openrouter client
    mock_openrouter = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "OpenRouter response text"
    mock_openrouter.chat.completions.create.return_value = mock_response
    
    # Temporarily set the client
    mocker.patch.object(llm_engine, "openrouter_client", mock_openrouter)
    # Ensure deepseek and gemini mocks don't run or are not called
    mocker.patch.object(llm_engine, "deepseek_client", None)
    mocker.patch.object(llm_engine, "gemini_clients", [])
    
    res = llm_engine.call_llm("test prompt")
    assert res == "OpenRouter response text"
    mock_openrouter.chat.completions.create.assert_called_once()

def test_call_llm_fallback_to_deepseek(mocker):
    # Mock openrouter to fail
    mock_openrouter = MagicMock()
    mock_openrouter.chat.completions.create.side_effect = Exception("OpenRouter error")
    
    # Mock deepseek to succeed
    mock_deepseek = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "DeepSeek response text"
    mock_deepseek.chat.completions.create.return_value = mock_response
    
    mocker.patch.object(llm_engine, "openrouter_client", mock_openrouter)
    mocker.patch.object(llm_engine, "deepseek_client", mock_deepseek)
    mocker.patch.object(llm_engine, "gemini_clients", [])
    
    # Mock sleep to avoid waiting during retries
    mocker.patch("time.sleep")
    
    res = llm_engine.call_llm("test prompt")
    assert res == "DeepSeek response text"
    assert mock_openrouter.chat.completions.create.call_count == 3  # Retries 3 times
    mock_deepseek.chat.completions.create.assert_called_once()

def test_call_llm_fallback_to_gemini(mocker):
    # Mock openrouter and deepseek to fail
    mock_openrouter = MagicMock()
    mock_openrouter.chat.completions.create.side_effect = Exception("OR error")
    
    mock_deepseek = MagicMock()
    mock_deepseek.chat.completions.create.side_effect = Exception("DS error")
    
    # Mock gemini to succeed
    mock_gemini_client = MagicMock()
    mock_gemini_response = MagicMock()
    mock_gemini_response.text = "Gemini response text"
    mock_gemini_client.models.generate_content.return_value = mock_gemini_response
    
    mocker.patch.object(llm_engine, "openrouter_client", mock_openrouter)
    mocker.patch.object(llm_engine, "deepseek_client", mock_deepseek)
    mocker.patch.object(llm_engine, "gemini_clients", [mock_gemini_client])
    
    mocker.patch("time.sleep")
    
    res = llm_engine.call_llm("test prompt")
    assert res == "Gemini response text"
    mock_gemini_client.models.generate_content.assert_called_once()

def test_call_llm_all_failed(mocker):
    # Mock all to fail
    mock_openrouter = MagicMock()
    mock_openrouter.chat.completions.create.side_effect = Exception("OR error")
    mock_deepseek = MagicMock()
    mock_deepseek.chat.completions.create.side_effect = Exception("DS error")
    mock_gemini_client = MagicMock()
    mock_gemini_client.models.generate_content.side_effect = Exception("Gemini error")
    
    mocker.patch.object(llm_engine, "openrouter_client", mock_openrouter)
    mocker.patch.object(llm_engine, "deepseek_client", mock_deepseek)
    mocker.patch.object(llm_engine, "gemini_clients", [mock_gemini_client])
    
    mocker.patch("time.sleep")
    
    res = llm_engine.call_llm("test prompt")
    assert res == ""
