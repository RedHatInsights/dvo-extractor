"""Submodule for testing ccx_data_pipeline.logging."""

from unittest.mock import MagicMock, patch

import pytest

from ccx_data_pipeline.logging import setup_watchtower


_INCOMPLETE_CW_CONFIGURATION = [
    # Missing one env var
    {
        "CW_AWS_ACCESS_KEY_ID": "AWS_KEY",
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "AWS_REGION_NAME": "a region",
        "CW_LOG_GROUP": "a group",
    },
    {
        "CW_AWS_ACCESS_KEY_ID": "AWS_KEY",
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "AWS_REGION_NAME": "a region",
        "CW_STREAM_NAME": "the stream",
    },
    {
        "CW_AWS_ACCESS_KEY_ID": "AWS_KEY",
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "CW_LOG_GROUP": "a group",
        "CW_STREAM_NAME": "the stream",
    },
    {
        "CW_AWS_ACCESS_KEY_ID": "AWS_KEY",
        "AWS_REGION_NAME": "a region",
        "CW_LOG_GROUP": "a group",
        "CW_STREAM_NAME": "the stream",
    },
    {
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "AWS_REGION_NAME": "a region",
        "CW_LOG_GROUP": "a group",
        "CW_STREAM_NAME": "the stream",
    },
    # All envs, but some empty
    {
        "CW_AWS_ACCESS_KEY_ID": "AWS_KEY",
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "AWS_REGION_NAME": "a region",
        "CW_LOG_GROUP": "a group",
        "CW_STREAM_NAME": "",
    },
    {
        "CW_AWS_ACCESS_KEY_ID": "  ",
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "AWS_REGION_NAME": "a region",
        "CW_LOG_GROUP": "a group",
        "CW_STREAM_NAME": "the stream",
    },
    {},
]


@pytest.mark.parametrize("fake_env", _INCOMPLETE_CW_CONFIGURATION)
@patch("ccx_data_pipeline.logging.Session", lambda **kwargs: None)
@patch("ccx_data_pipeline.logging.CloudWatchLogHandler", lambda **kwargs: None)
@patch("ccx_data_pipeline.logging.logging.getLogger")
def test_setup_watchtower_misconfigured(get_logger_mock, fake_env):
    """Test that no watchtower is used when environment is not configured."""
    with patch.dict("ccx_data_pipeline.logging.os.environ", fake_env, clear=True):
        setup_watchtower()
        assert get_logger_mock.called is False


@patch("ccx_data_pipeline.logging.Session")
@patch("ccx_data_pipeline.logging.CloudWatchLogHandler")
@patch("ccx_data_pipeline.logging.logging.getLogger")
def test_setup_watchtower(get_logger_mock, log_handler_init_mock, session_init_mock):
    """Test logger configuration. Mocking everything to avoid network failures."""
    # logging.getLogger return a mocked log
    logger_mock = MagicMock()
    get_logger_mock.return_value = logger_mock

    # Session init should return a mock to check CloudWatchLogHandler args
    session_mock = MagicMock()
    session_init_mock.return_value = session_mock

    valid_env = {
        "CW_AWS_ACCESS_KEY_ID": "AWS_KEY",
        "CW_AWS_SECRET_ACCESS_KEY": "AWS_SECRET",
        "AWS_REGION_NAME": "a region",
        "CW_LOG_GROUP": "a group",
        "CW_STREAM_NAME": "the stream",
    }

    with patch.dict("ccx_data_pipeline.logging.os.environ", valid_env):
        setup_watchtower()
        session_init_mock.assert_called_with(
            aws_access_key_id=valid_env["CW_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=valid_env["CW_AWS_SECRET_ACCESS_KEY"],
            region_name=valid_env["AWS_REGION_NAME"],
        )
        log_handler_init_mock.assert_called_with(
            boto3_session=session_mock,
            log_group=valid_env["CW_LOG_GROUP"],
            stream_name=valid_env["CW_STREAM_NAME"],
        )
