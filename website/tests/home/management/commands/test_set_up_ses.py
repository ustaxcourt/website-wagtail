"""Tests for home/management/commands/set_up_ses.py"""

from io import StringIO
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from home.management.commands.set_up_ses import Command


def _make_cmd():
    cmd = Command.__new__(Command)
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()
    cmd.style = MagicMock()
    cmd.style.SUCCESS = lambda s: s
    cmd.style.ERROR = lambda s: s
    cmd.style.WARNING = lambda s: s
    cmd.ses_client = MagicMock()
    cmd.route53_client = MagicMock()
    return cmd


class TestSetUpSesInit:
    def test_create_boto_client_returns_none_on_exception(self):
        with patch(
            "home.management.commands.set_up_ses.boto3.client",
            side_effect=Exception("AWS error"),
        ):
            cmd = Command.__new__(Command)
            cmd.stderr = StringIO()
            cmd.style = MagicMock()
            cmd.style.ERROR = lambda s: s
            result = cmd._create_boto_client("ses")
            assert result is None

    def test_create_boto_client_returns_client_on_success(self):
        mock_client = MagicMock()
        with patch(
            "home.management.commands.set_up_ses.boto3.client", return_value=mock_client
        ):
            cmd = Command.__new__(Command)
            cmd.stderr = StringIO()
            cmd.style = MagicMock()
            cmd.style.ERROR = lambda s: s
            result = cmd._create_boto_client("ses")
            assert result is mock_client


class TestSetUpSesHandle:
    def test_handle_exits_when_no_domain_name(self):
        cmd = _make_cmd()
        import os

        os.environ.pop("DOMAIN_NAME", None)
        with patch.dict("os.environ", {}, clear=True):
            cmd.handle()

    def test_handle_exits_when_ses_client_is_none(self):
        cmd = _make_cmd()
        cmd.ses_client = None
        with patch.dict("os.environ", {"DOMAIN_NAME": "example.com"}):
            cmd.handle()

    def test_handle_exits_when_route53_client_is_none(self):
        cmd = _make_cmd()
        cmd.route53_client = None
        with patch.dict("os.environ", {"DOMAIN_NAME": "example.com"}):
            cmd.handle()

    def test_handle_calls_get_dkim_tokens_when_clients_present(self):
        cmd = _make_cmd()
        with patch.dict("os.environ", {"DOMAIN_NAME": "example.com"}):
            with patch.object(cmd, "_get_dkim_tokens", return_value=None) as mock_get:
                cmd.handle()
                mock_get.assert_called_once_with("example.com")

    def test_handle_calls_add_records_when_tokens_returned(self):
        cmd = _make_cmd()
        with patch.dict("os.environ", {"DOMAIN_NAME": "example.com"}):
            with patch.object(
                cmd, "_get_dkim_tokens", return_value=["token1", "token2"]
            ):
                with patch.object(
                    cmd, "_add_records_to_route53", return_value=False
                ) as mock_add:
                    cmd.handle()
                    mock_add.assert_called_once()

    def test_handle_calls_check_verification_when_records_added(self):
        cmd = _make_cmd()
        with patch.dict("os.environ", {"DOMAIN_NAME": "example.com"}):
            with patch.object(cmd, "_get_dkim_tokens", return_value=["token1"]):
                with patch.object(cmd, "_add_records_to_route53", return_value=True):
                    with patch.object(cmd, "_check_verification_status") as mock_check:
                        cmd.handle()
                        mock_check.assert_called_once_with("example.com")


class TestGetDkimTokens:
    def test_returns_tokens_on_success(self):
        cmd = _make_cmd()
        cmd.ses_client.verify_domain_dkim.return_value = {"DkimTokens": ["abc", "def"]}
        result = cmd._get_dkim_tokens("example.com")
        assert result == ["abc", "def"]

    def test_returns_empty_list_when_no_tokens(self):
        cmd = _make_cmd()
        cmd.ses_client.verify_domain_dkim.return_value = {"DkimTokens": []}
        result = cmd._get_dkim_tokens("example.com")
        assert result == []

    def test_returns_none_on_client_error(self):
        cmd = _make_cmd()
        error_response = {"Error": {"Code": "400", "Message": "Bad request"}}
        cmd.ses_client.verify_domain_dkim.side_effect = ClientError(
            error_response, "verify_domain_dkim"
        )
        result = cmd._get_dkim_tokens("example.com")
        assert result is None


class TestAddRecordsToRoute53:
    def test_returns_true_when_no_tokens(self):
        cmd = _make_cmd()
        result = cmd._add_records_to_route53("example.com", [])
        assert result is True

    def test_returns_false_when_zone_not_found(self):
        cmd = _make_cmd()
        cmd.route53_client.list_hosted_zones.return_value = {
            "HostedZones": [{"Id": "/hostedzone/Z1", "Name": "other.com."}]
        }
        result = cmd._add_records_to_route53("example.com", ["token1"])
        assert result is False

    def test_returns_true_when_records_added_successfully(self):
        cmd = _make_cmd()
        cmd.route53_client.list_hosted_zones.return_value = {
            "HostedZones": [{"Id": "/hostedzone/Z1", "Name": "example.com."}]
        }
        cmd.route53_client.change_resource_record_sets.return_value = {
            "ChangeInfo": {"Id": "/change/ABC123"}
        }
        result = cmd._add_records_to_route53("example.com", ["token1"])
        assert result is True

    def test_returns_false_on_client_error(self):
        cmd = _make_cmd()
        error_response = {"Error": {"Code": "400", "Message": "Access denied"}}
        cmd.route53_client.list_hosted_zones.side_effect = ClientError(
            error_response, "list_hosted_zones"
        )
        result = cmd._add_records_to_route53("example.com", ["token1"])
        assert result is False


class TestCheckVerificationStatus:
    def test_returns_on_success_status(self):
        cmd = _make_cmd()
        cmd.ses_client.get_identity_dkim_attributes.return_value = {
            "DkimAttributes": {"example.com": {"DkimVerificationStatus": "Success"}}
        }
        with patch("home.management.commands.set_up_ses.time.sleep"):
            cmd._check_verification_status("example.com", retries=1, delay=1)
        # No exception = passed

    def test_returns_on_failed_status(self):
        cmd = _make_cmd()
        cmd.ses_client.get_identity_dkim_attributes.return_value = {
            "DkimAttributes": {"example.com": {"DkimVerificationStatus": "Failed"}}
        }
        with patch("home.management.commands.set_up_ses.time.sleep"):
            cmd._check_verification_status("example.com", retries=1, delay=1)

    def test_returns_on_client_error(self):
        cmd = _make_cmd()
        error_response = {"Error": {"Code": "400", "Message": "Error"}}
        cmd.ses_client.get_identity_dkim_attributes.side_effect = ClientError(
            error_response, "get_identity_dkim_attributes"
        )
        with patch("home.management.commands.set_up_ses.time.sleep"):
            cmd._check_verification_status("example.com", retries=1, delay=1)

    def test_handles_missing_attributes(self):
        cmd = _make_cmd()
        cmd.ses_client.get_identity_dkim_attributes.return_value = {
            "DkimAttributes": {}
        }
        with patch("home.management.commands.set_up_ses.time.sleep"):
            cmd._check_verification_status("example.com", retries=2, delay=1)
