from http.server import BaseHTTPRequestHandler
from urllib import parse
import requests

class TriviaHandler(BaseHTTPRequestHandler):
    """A simple HTTP request handler for fetching trivia questions."""

    def do_GET(self):
        """Handles GET requests."""

        # Parse URL and extract query parameters
        url_components = parse.urlsplit(self.path)
        query_params = dict(parse.parse_qsl(url_components.query))

        # Base URL for the trivia API
        base_url = "https://opentdb.com/api.php"

        # List to store fetched questions
        questions = []

        # Counter for question numbering
        question_count = 1

        try:
            if 'category' in query_params:
                category_id = int(query_params['category'])

                if category_id == 33:
                    # Handle special case for category 33
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b"You have selected category 33, which is not available.\n")
                    return

                # Fetch category data from the API
                response = requests.get("https://opentdb.com/api_category.php")
                categories = response.json()['trivia_categories']

                # Find category name by ID
                category_name = next((c['name'] for c in categories if c['id'] == category_id), "")

                if category_name:
                    # Fetch questions based on category and amount
                    amount = int(query_params.get('amount', 10))
                    response = requests.get(f"{base_url}?amount={amount}&category={category_id}")
                    data = response.json()

                    if 'results' in data:
                        questions.append(f"Category: {category_name}\n\n")

                        # Format questions and answers
                        for q in data['results']:
                            question = q['question']
                            correct_answer = q['correct_answer']
                            questions.append(f"{question_count}. {question} - {correct_answer}\n\n")
                            question_count += 1
                    else:
                        questions.append("No questions found for this category.")
                else:
                    self.send_error(400, "Invalid category ID")
                    return

            elif 'amount' in query_params:
                # Handle request for random questions
                amount = min(int(query_params['amount']), 50)
                response = requests.get(f"{base_url}?amount={amount}")
                data = response.json()

                if 'results' in data:
                    questions.append(f"Amount: {amount}\n\n")

                    # Format questions and answers
                    for q in data['results']:
                        question = q['question']
                        correct_answer = q['correct_answer']
                        questions.append(f"{question_count}. {question} - {correct_answer}\n\n")
                        question_count += 1

            elif url_components.path == "/api/questions":
                # Handle request to /api/questions endpoint
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Welcome to the trivia API!")
                return

            else:
                self.send_error(400, "Missing required parameters")
                return

            # Send successful response with questions
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            if questions:
                response_msg = "\n".join(questions)
                self.wfile.write(response_msg.encode())
            else:
                self.wfile.write(b"No questions found")

        except ValueError:
            self.send_error(400, "Invalid parameter value")
            return


