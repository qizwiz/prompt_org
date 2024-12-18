import io
from unittest.mock import patch

import pandas as pd
from main import (call_ai_api, generate_api_payload, parse_api_response,
                  safe_load_data, upload_and_process_file)


def test_parse_api_response_with_valid_data():
    valid_response = """
    [
        {"Letter": "A", "PromptName": "Test1", "Categories": "Category1", "PromptText": "This is a test."},
        {"Letter": "B", "PromptName": "Test2", "Categories": "Category2", "PromptText": "Another test."}
    ]
    """
    result = parse_api_response(valid_response)
    assert len(result) == 2
    assert result[0]["Letter"] == "A"


def test_parse_api_response_with_invalid_json():
    invalid_response = "This is not a valid JSON."
    result = parse_api_response(invalid_response)
    assert result == [], "Result should be empty for invalid JSON."


def test_parse_api_response_with_partial_invalid_objects():
    mixed_response = """
    [
        {"Letter": "A", "PromptName": "Test1", "Categories": "Category1", "PromptText": "Valid."},
        {"InvalidKey": "Invalid", "PromptName": "Test2", "Categories": "Category2", "PromptText": "Invalid."}
    ]
    """
    result = parse_api_response(mixed_response)
    assert len(result) == 1, "Only valid objects should be included."
    assert result[0]["Letter"] == "A"


# Test: Schema Mismatch or Invalid Columns
def test_safe_load_data_with_schema_mismatch():
    sample_data = pd.DataFrame({"InvalidColumn": [1, 2, 3]})
    with patch("pandas.read_parquet", return_value=sample_data):
        result = safe_load_data()
        assert result.empty, "DataFrame should be empty when schema does not match."


# Test: Missing Parquet File
def test_safe_load_data_with_missing_file():
    with patch("os.path.exists", return_value=False):
        result = safe_load_data()
        assert result.empty, "DataFrame should be empty when file does not exist."


# Test: Valid Parquet File
@patch("pandas.read_parquet")
@patch("os.path.exists", return_value=True)
def test_safe_load_data_with_valid_file(
    _, mock_read_parquet
):  # "_" for unused mock_exists
    sample_data = pd.DataFrame(
        {
            "Categories": ["TestCategory"],
            "PromptName": ["TestPrompt"],
            "PromptText": ["This is a test prompt."],
            "Model": ["TestModel"],
        }
    )
    mock_read_parquet.return_value = sample_data

    result = safe_load_data()
    pd.testing.assert_frame_equal(result, sample_data)


# Test 1: Validate `load_data()` Functionality
@patch("pandas.read_parquet")
@patch("os.path.exists", return_value=True)
def test_load_data_with_existing_parquet(
    _, mock_read_parquet
):  # "_" for unused mock_exists
    sample_data = pd.DataFrame(
        {
            "Categories": ["Category1", "Category2"],
            "PromptName": ["Test Prompt 1", "Test Prompt 2"],
            "PromptText": ["Prompt text 1", "Prompt text 2"],
            "Model": ["model1", "model2"],
        }
    )
    mock_read_parquet.return_value = sample_data

    result = safe_load_data()
    pd.testing.assert_frame_equal(result, sample_data)


def test_load_data_with_no_file():
    with patch("os.path.exists", return_value=False):
        result = safe_load_data()
        assert result.empty


# Test 2: Validate `parse_api_response()`
def test_parse_api_response_valid_json():
    response_text = """
    [
        {"Letter": "A", "PromptName": "Example1", "Categories": "Cat1", "PromptText": "Sample text1"},
        {"Letter": "B", "PromptName": "Example2", "Categories": "Cat2", "PromptText": "Sample text2"}
    ]
    """
    result = parse_api_response(response_text)
    assert len(result) == 2
    assert result[0]["Letter"] == "A"


def test_parse_api_response_invalid_json():
    response_text = "This is invalid JSON."
    result = parse_api_response(response_text)
    assert result == []


# Test 3: Mock API Call
@patch("requests.post")
def test_generate_api_call(requests_mock):
    mock_response = {
        "choices": [
            {"message": {"content": '[{"Letter": "C", "PromptName": "Generated1"}]'}}
        ]
    }
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = mock_response

    payload = generate_api_payload("Test prompt", "gpt-4", 500, 0.7)
    result = call_ai_api(payload)

    assert requests_mock.called
    assert result == mock_response


# Test 4: File Upload Logic
@patch("pandas.read_csv")
@patch("pandas.DataFrame.to_parquet")
def test_upload_and_process_file(_, mock_read_csv):  # "_" for unused mock_to_parquet
    mock_data = pd.DataFrame(
        {
            "Letter": ["A"],
            "Prompt Name": ["NewPrompt"],
            "Category": ["NewCat"],
            "Prompt Text": ["New Text"],
        }
    )
    mock_read_csv.return_value = mock_data

    uploaded_file = io.StringIO(
        "Letter,Prompt Name,Category,Prompt Text\nA,NewPrompt,NewCat,New Text"
    )

    result = upload_and_process_file(uploaded_file, "CSV")
    assert not result.empty
    assert result.iloc[0]["PromptName"] == "NewPrompt"
