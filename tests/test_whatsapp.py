import unittest

from rasa_whatsapp_connector.whatsapp import RasaToWhatsappConverter


class TestWhatsappCloudApiConverter(unittest.TestCase):
    """
    Tests the WhatsappCloudApiConverter class
    """
    def setUp(self):
        self._converter = RasaToWhatsappConverter('987654321', 'sample_token')

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

        expected = {
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

        expected = {
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

        self.assertEqual(
            self._converter.prepare_message(to, text, buttons_above_limit),
            expected,
        )

        self.assertNotEqual(
            self._converter.prepare_message(to, text, buttons_below_limit),
            expected,
        )
