"""El ejemplo de OpenAI solo anuncia consultas MCP. Sin acceso a red."""
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / "examples" / "openai_mcp_readonly.py"
spec = importlib.util.spec_from_file_location("openai_readonly", path)
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class OpenAIReadOnlyTests(unittest.TestCase):
    def test_missing_credentials_fail_before_request(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Faltan variables"):
                example.build_request()

    def test_only_read_tools_are_allowed(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-openai", "VAPI_PRIVATE_API_KEY": "fake-vapi", "OPENAI_MODEL": "selected-by-user"}, clear=True):
            req = example.build_request()
        data = json.loads(req.data)
        tool = data["tools"][0]
        self.assertEqual(set(tool["allowed_tools"]), {"list_assistants", "list_phone_numbers"})
        self.assertNotIn("create_call", tool["allowed_tools"])
        self.assertEqual(tool["authorization"], "fake-vapi")
        self.assertEqual(req.get_header("Authorization"), "Bearer fake-openai")
        self.assertEqual(data["model"], "selected-by-user")

    def test_explicit_model_required(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-openai", "VAPI_PRIVATE_API_KEY": "fake-vapi"}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENAI_MODEL"):
                example.build_request()


if __name__ == "__main__":
    unittest.main()
