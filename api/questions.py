from http.server import BaseHTTPRequestHandler 
from urllib import parse
import requests 
import json


class handler(BaseHTTPRequestHandler):
    """ A simple HTTP request handler that fetches trivia questions."""

    def do_GET(self):
        """ Handles GET requests."""

        # Base URL for the trivia API with predefined parameters
        api_url = "https://opentdb.com/api.php?amount=20&category=9&difficulty=easy&type=boolean"

        try:
            # Fetching questions from the API
            response = requests.get(api_url)
            data = response.json()

            # Checking if 'results' key exists in the response
            if 'results' in data:
                # Prepare response message with each question on a new line
                questions = []
                for index, q in enumerate(data['results'], start=1):
                    question = q['question']
                    correct_answer = q['correct_answer']
                    questions.append(f"{index}. {question} - {correct_answer}")

                response_msg = "\n\n".join(questions)

                # Sending the response
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(response_msg.encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"No questions found")

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

        return