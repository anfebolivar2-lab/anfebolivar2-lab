"""Pruebas sin red: nunca realizan llamadas ni requieren credenciales."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("vapi_phone", ROOT / "scripts" / "vapi_phone.py")
vapi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vapi)


class CallGuardTests(unittest.TestCase):
    args = ["create-call", "--assistant-id", "test-assistant", "--phone-number-id", "test-phone", "--to", "+12025550123"]

    def run_cli(self, args, env=None):
        with patch.dict(os.environ, env or {}, clear=True), contextlib.redirect_stdout(io.StringIO()) as out:
            with contextlib.redirect_stderr(io.StringIO()) as err:
                result = vapi.main(args)
        return result, out.getvalue(), err.getvalue()

    @patch.object(vapi, "request_json")
    def test_default_dry_run_never_uses_network_or_needs_key(self, request):
        result, output, _ = self.run_cli(self.args)
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output)["mode"], "SIMULACION_SIN_RED")
        request.assert_not_called()

    @patch.object(vapi, "request_json")
    def test_execution_blocked_without_allowlist(self, request):
        with self.assertRaises(SystemExit):
            self.run_cli(self.args + ["--execute", "--confirm-destination", "+12025550123"])
        request.assert_not_called()

    @patch.object(vapi, "request_json")
    def test_execution_blocked_without_matching_confirmation(self, request):
        with self.assertRaises(SystemExit):
            self.run_cli(self.args + ["--execute", "--confirm-destination", "+12025550124"],
                         {"ALLOWED_TEST_NUMBERS": "+12025550123", "VAPI_PRIVATE_API_KEY": "fake-test-key"})
        request.assert_not_called()

    @patch.object(vapi, "request_json")
    def test_execution_blocked_without_private_key(self, request):
        with self.assertRaises(SystemExit):
            self.run_cli(self.args + ["--execute", "--confirm-destination", "+12025550123"],
                         {"ALLOWED_TEST_NUMBERS": "+12025550123"})
        request.assert_not_called()

    @patch.object(vapi, "request_json", return_value={"id": "call-test", "status": "queued", "secret": "hidden"})
    def test_authorized_execution_sends_exactly_one_request(self, request):
        code, output, _ = self.run_cli(self.args + ["--execute", "--confirm-destination", "+12025550123"],
                                    {"ALLOWED_TEST_NUMBERS": "+12025550123", "VAPI_PRIVATE_API_KEY": "fake-test-key"})
        self.assertEqual(code, 0)
        request.assert_called_once_with("POST", "/call", "fake-test-key", {
            "assistantId": "test-assistant", "phoneNumberId": "test-phone", "customer": {"number": "+12025550123"}})
        self.assertEqual(json.loads(output), {"id": "call-test", "status": "queued"})
        self.assertNotIn("fake-test-key", output)

    @patch.object(vapi, "request_json")
    def test_invalid_number_rejected_before_network(self, request):
        with self.assertRaises(SystemExit):
            self.run_cli(["create-call", "--assistant-id", "a", "--phone-number-id", "p", "--to", "300 123"])
        request.assert_not_called()

    @patch.object(vapi, "urlopen", side_effect=URLError("test timeout"))
    def test_uncertain_post_is_not_retried(self, network):
        with self.assertRaisesRegex(RuntimeError, "podría haberse creado"):
            vapi.request_json("POST", "/call", "fake-test-key", {"test": True})
        self.assertEqual(network.call_count, 1)

    @patch.object(vapi, "request_json", return_value={"id": "call-one", "status": "ended"})
    def test_get_call_reads_without_exposing_private_fields(self, request):
        code, output, _ = self.run_cli(["get-call", "call-one"], {"VAPI_PRIVATE_API_KEY": "fake-test-key"})
        self.assertEqual(code, 0)
        request.assert_called_once_with("GET", "/call/call-one", "fake-test-key")
        self.assertEqual(json.loads(output)["id"], "call-one")

    def test_call_id_is_encoded_as_single_path_component(self):
        with patch.object(vapi, "request_json", return_value={"id": "test"}) as request:
            self.run_cli(["get-call", "bad/id?value"], {"VAPI_PRIVATE_API_KEY": "fake-test-key"})
            self.assertEqual(request.call_args.args[1], "/call/bad%2Fid%3Fvalue")


if __name__ == "__main__":
    unittest.main()
