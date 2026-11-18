import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from main import app


class ComplaintWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def submit(self, complaint):
        return self.client.post("/api/v1/complaints", json={"complaint_text": complaint})

    def resume(self, thread_id, approved):
        return self.client.post(
            f"/api/v1/reviews/{thread_id}/resume",
            json={"approved": approved},
        )

    @patch("graph.create_ticket")
    @patch("graph.find_known_resolution", return_value="Pair the headphones again.")
    def test_known_resolution(self, lookup, create_ticket):
        response = self.submit("My headphones are not pairing.")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Pair the headphones again.")
        self.assertIsNone(response.json()["ticket_ref"])
        lookup.assert_called_once()
        create_ticket.assert_not_called()

    @patch("graph.create_ticket", return_value=42)
    @patch("graph.find_known_resolution", return_value=None)
    def test_new_ticket(self, lookup, create_ticket):
        response = self.submit("My tablet arrived cracked.")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ticket_ref"], "TKT-42")
        self.assertEqual(create_ticket.call_args.kwargs["priority"], "high")
        lookup.assert_called_once()

    @patch("graph.create_ticket", return_value=43)
    @patch("graph.find_known_resolution")
    def test_approve_review(self, lookup, create_ticket):
        paused = self.submit("My tablet arrived cracked. I will go to consumer court.")
        self.assertEqual(paused.json()["status"], "human_review_required")
        create_ticket.assert_not_called()
        lookup.assert_not_called()

        thread_id = paused.json()["thread_id"]
        resumed = self.resume(thread_id, True)
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()["ticket_ref"], "TKT-43")
        self.assertEqual(create_ticket.call_args.kwargs["priority"], "critical")
        self.assertEqual(self.resume(thread_id, True).status_code, 404)
        create_ticket.assert_called_once()

    @patch("graph.create_ticket")
    def test_decline_review(self, create_ticket):
        paused = self.submit("I will take legal action.")
        resumed = self.resume(paused.json()["thread_id"], False)
        self.assertEqual(resumed.status_code, 200)
        self.assertIsNone(resumed.json()["ticket_ref"])
        self.assertEqual(resumed.json()["response"], "Reviewer declined escalation.")
        create_ticket.assert_not_called()

    def test_validation(self):
        self.assertEqual(self.submit("").status_code, 422)
        self.assertEqual(self.resume("unknown", "yes").status_code, 422)
        self.assertEqual(self.resume("unknown", True).status_code, 404)
