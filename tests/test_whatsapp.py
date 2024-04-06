from typing import Dict, Any

import unittest

from mock import patch

from rasa_whatsapp_connector.whatsapp import RasaToWhatsappConverter


class TestWhatsappCloudApiConverter(unittest.TestCase):
    """
    Tests the WhatsappCloudApiConverter class
    """
    def setUp(self):
        self._phone_identifier = '987654321'
        self._token = 'sample_token'
        self._graphql_api_version = 'v18.0'
        self._timeout = 1
        self._converter = RasaToWhatsappConverter(
            self._phone_identifier,
            self._token,
            self._graphql_api_version,
            self._timeout,
        )

    def _get_buttons_below_limit_interactive(self):
        return [
            {
                'title': 'Test Button 1',
                'payload': 'Payload Button 1'
            },
            {
                'title': 'Test Button 2',
                'payload': 'Payload Button 2'
            },
            {
                'title': 'Test Button 3',
                'payload': 'Payload Button 3'
            },
        ]

    def _get_expected_buttons_below_limit_interactive(self, to: str, text: str):
        return {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'interactive',
            'interactive':
                {
                    'type': 'button',
                    'body': {
                        "text": text
                    },
                    'action':
                        {
                            'buttons':
                                [
                                    {
                                        'type': 'reply',
                                        'reply':
                                            {
                                                'id': 'Payload Button 1',
                                                'title': 'Test Button 1'
                                            }
                                    }, {
                                        'type': 'reply',
                                        'reply':
                                            {
                                                'id': 'Payload Button 2',
                                                'title': 'Test Button 2'
                                            }
                                    }, {
                                        'type': 'reply',
                                        'reply':
                                            {
                                                'id': 'Payload Button 3',
                                                'title': 'Test Button 3'
                                            }
                                    }
                                ]
                        }
                }
        }

    def _get_expected_buttons_above_limit_interactive(self, to: str, text: str):
        return {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'interactive',
            'interactive':
                {
                    'type': 'list',
                    'body': {
                        "text": text
                    },
                    'action':
                        {
                            'button':
                                'Select',
                            'sections':
                                [
                                    {
                                        'title':
                                            'Select',
                                        'rows':
                                            [
                                                {
                                                    'id': 'Payload Button 1',
                                                    'title': 'Test Button 1'
                                                }, {
                                                    'id': 'Payload Button 2',
                                                    'title': 'Test Button 2'
                                                }, {
                                                    'id': 'Payload Button 3',
                                                    'title': 'Test Button 3'
                                                }, {
                                                    'id': 'Payload Button 4',
                                                    'title': 'Test Button 4'
                                                }, {
                                                    'id': 'Payload Button 5',
                                                    'title': 'Test Button 5'
                                                }, {
                                                    'id': 'Payload Button 6',
                                                    'title': 'Test Button 6'
                                                }
                                            ],
                                    }
                                ]
                        }
                }
        }

    def _get_buttons_above_limit_interactive(self):
        return self._get_buttons_below_limit_interactive() + [
            {
                'title': 'Test Button 4',
                'payload': 'Payload Button 4'
            },
            {
                'title': 'Test Button 5',
                'payload': 'Payload Button 5'
            },
            {
                'title': 'Test Button 6',
                'payload': 'Payload Button 6'
            },
        ]

    def test_prepare_text_message(self):
        """
        Tests preparing a text message
        """
        to = "123456789"
        text = "This is a sample text message"

        expected = {
            'messaging_product': 'whatsapp',
            'to': to,
            'text': {
                'body': text
            }
        }

        self.assertEqual(
            self._converter.prepare_message(to, text),
            expected,
        )

    def test_prepare_button_message(self):
        """
        Tests preparing a button message
        """
        to = "123456789"
        text = "This is a sample text message"

        buttons_below_limit = self._get_buttons_below_limit_interactive()
        buttons_above_limit = self._get_buttons_above_limit_interactive()

        expected = self._get_expected_buttons_below_limit_interactive(to, text)

        self.assertEqual(
            self._converter.prepare_message(to, text, buttons_below_limit),
            expected,
        )

        self.assertNotEqual(
            self._converter.prepare_message(to, text, buttons_above_limit),
            expected,
        )

    def test_prepare_list_message(self):
        """
        Tests preparing a list message
        """
        to = "123456789"
        text = "This is a sample text message"

        buttons_below_limit = self._get_buttons_below_limit_interactive()
        buttons_above_limit = self._get_buttons_above_limit_interactive()

        expected = self._get_expected_buttons_above_limit_interactive(to, text)

        self.assertEqual(
            self._converter.prepare_message(to, text, buttons_above_limit),
            expected,
        )

        self.assertNotEqual(
            self._converter.prepare_message(to, text, buttons_below_limit),
            expected,
        )

    @patch('requests.post')
    def test_send_message(self, post_mock):
        """
        Tests sending a message
        """
        to = "123456789"
        text = "This is a sample text message"
        buttons_below_limit = self._get_buttons_below_limit_interactive()
        expected = self._get_expected_buttons_below_limit_interactive(to, text)
        expected_headers = {'Authorization': 'Bearer sample_token'}
        expected_url = f"""
            https://graph.facebook.com/{self._graphql_api_version}{self._phone_identifier}/messages
        """.strip()

        self._converter.send_message(to, text, buttons_below_limit)

        post_mock.assert_called_with(
            expected_url,
            json=expected,
            headers=expected_headers,
            timeout=self._timeout,
        )

    def test_get_message_from_whatsapp_hook_invalid_value(self):
        """
        Tests invalid value received from a whatsapp hook call
        """
        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            {},
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            {"entry": []},
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            {"entry": [{}]},
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            {"entry": [{
                "changes": []
            }]},
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            {"entry": [{
                "changes": [{}]
            }]},
        )

    def _prepare_whatsapp_value(self, data: Dict[str, Any]):
        return {"entry": [{"changes": [{"value": data}]}]}

    def test_get_message_from_whatsapp_hook_invalid_message(self):
        """
        Tests invalid message received from a whatsapp hook call
        """
        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value({}),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value({"messages": []}),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value({"messages": [{}]}),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value({"messages": [{
                "from": "12345678"
            }]}),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value({"messages": [{
                "from": "12345678"
            }]}),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value(
                {"messages": [{
                    "from": "12345678",
                    "type": "text"
                }]}
            ),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value(
                {"messages": [{
                    "from": "12345678",
                    "type": "interactive"
                }]}
            ),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value(
                {
                    "messages":
                        [
                            {
                                "from": "12345678",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply"
                                }
                            }
                        ]
                }
            ),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value(
                {
                    "messages":
                        [
                            {
                                "from": "12345678",
                                "type": "interactive",
                                "interactive":
                                    {
                                        "type": "button_reply",
                                        "button_reply": {}
                                    }
                            }
                        ]
                }
            ),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value(
                {
                    "messages":
                        [
                            {
                                "from": "12345678",
                                "type": "interactive",
                                "interactive": {
                                    "type": "list_reply"
                                }
                            }
                        ]
                }
            ),
        )

        self.assertRaises(
            ValueError,
            self._converter.get_message_from_whatsapp_hook,
            self._prepare_whatsapp_value(
                {
                    "messages":
                        [
                            {
                                "from": "12345678",
                                "type": "interactive",
                                "interactive":
                                    {
                                        "type": "list_reply",
                                        "list_reply": {}
                                    }
                            }
                        ]
                }
            ),
        )

    def _prepare_whatsapp_message(self, data: Dict[str, Any]):
        return self._prepare_whatsapp_value({"messages": [data]})

    def test_get_message_from_whatsapp_hook_valid_message(self):
        """
        Tests valid received from a whatsapp hook call
        """

        text_message = self._prepare_whatsapp_message(
            {
                "from": "12345678",
                "type": "text",
                "text": {
                    "body": "sample text message"
                }
            }
        )

        rasa_text_message = self._converter.get_message_from_whatsapp_hook(
            text_message
        )

        self.assertEqual(rasa_text_message["sender_id"], "12345678")
        self.assertEqual(rasa_text_message["text"], "sample text message")
        self.assertDictEqual(rasa_text_message["metadata"], {})

        button_message = self._prepare_whatsapp_message(
            {
                "from": "12345678",
                "type": "interactive",
                "interactive":
                    {
                        "type": "button_reply",
                        "button_reply": {
                            "id": "sample_button_id"
                        }
                    }
            }
        )

        rasa_button_message = self._converter.get_message_from_whatsapp_hook(
            button_message
        )

        self.assertEqual(rasa_button_message["sender_id"], "12345678")
        self.assertEqual(rasa_button_message["text"], "sample_button_id")
        self.assertDictEqual(rasa_button_message["metadata"], {})

        list_message = self._prepare_whatsapp_message(
            {
                "from": "12345678",
                "type": "interactive",
                "interactive":
                    {
                        "type": "list_reply",
                        "list_reply": {
                            "id": "sample_list_id"
                        }
                    }
            }
        )

        rasa_list_message = self._converter.get_message_from_whatsapp_hook(
            list_message
        )

        self.assertEqual(rasa_list_message["sender_id"], "12345678")
        self.assertEqual(rasa_list_message["text"], "sample_list_id")
        self.assertDictEqual(rasa_list_message["metadata"], {})
