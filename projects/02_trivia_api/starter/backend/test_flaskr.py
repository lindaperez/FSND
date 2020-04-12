import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Create error handlers for all expected errors including
    # 400 Bad Request Error.
    # 404 Not Found,
    # Unprocessable Entity 422 x status code occurs when a request is well-formed, however,
    # due to semantic errors it is unable to be processed.
    # 500 Internal Server Error

    # Test Functionality

    # Test List of Categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    # Test List of Questions
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], '')
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    # Test Pagination
    def test_verify_pagination(self):
        res = self.client().get('/questions?page=1')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], '')
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        if data['total_questions'] > 10:
            self.assertEqual(len(data['questions']), 10)

    # Test add question
    def test_add_question(self):
        res = self.client().post('/questions/add',
                                 json={'question': 'Men who put first foot at the moon',
                                       'answer': 'Neil Amstrong', 'category': 4, 'difficulty': 4})

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['question'],'Men who put first foot at the moon')
        self.assertEqual(data['answer'],'Neil Amstrong')
        self.assertEqual(data['category'],4)
        self.assertEqual(data['difficulty'],4)


    # Test play trivia
    def test_play_game(self):
        res = self.client().post('/play',
                                 json={'quiz_category': {'id': '1', 'type': 'Science'}, 'previous_questions': []})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['category'],1)

    # Test delete element by id
    """
    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 2).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)    
        
    """

    def test_search_by_term(self):
        res = self.client().post('/questions',
                                 json={'searchTerm': 'What'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)


    # 404 NOT FOUND: URL wrote incorrectly.

    def test_verify_404_categories(self):
        res = self.client().get('/categori')
        print(res)
        self.assertEqual(res.status_code, 404)

    def test_verify_404_questions(self):
        res = self.client().get('/questio')
        self.assertEqual(res.status_code, 404)

    def test_verify_404_delete_question_by_id(self):
        res = self.client().delete('/questio/1')
        self.assertEqual(res.status_code, 404)

    def test_verify_404_question_by_category(self):
        res = self.client().get('/categories/1/quesons')
        self.assertEqual(res.status_code, 404)

    def test_verify_404_add_question(self):
        res = self.client().post('/add')
        self.assertEqual(res.status_code, 404)

    def test_404_play_game(self):
        res = self.client().post('/play/', json={'quiz_category': 1, 'previous_questions': []})
        self.assertEqual(res.status_code, 404)

    def test_404_search_by_term(self):
        res = self.client().post('/question',
                                 json={'searchTerm': 'What'})
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    # 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.

    # Arg quest incorrect
    def test_verify_400_questions(self):
        res = self.client().get('/questions', json={'question': 'question??'})
        self.assertEqual(res.status_code, 400)

    # Arg cat incorrect
    def test_verify_categories(self):
        res = self.client().get('/categories', json={'cat': 1})
        self.assertEqual(res.status_code, 400)
 

    # Args required, incorrect
    def test_verify_add_question(self):
        res = self.client().post('/questions/add')
        self.assertEqual(res.status_code, 400)

    # 422 Semantic Incorrect

    # Test Delete, Id doesnt exist
    def test_verify_422_delete_question_by_id(self):
        res = self.client().delete('/questions/1')
        self.assertEqual(res.status_code, 422)

    # Test Empty answer
    def test_verify_422_add_question(self):
        res = self.client().post('/questions/add',
                                 json={'question': 'Men who put first foot at the moon',
                                       'answer': '', 'category': 4, 'difficulty': 4})
        self.assertEqual(res.status_code, 422)

    # 500

    # Bad args type (quiz_category) should be a dict
    def test_error_500_play_game(self):
        res = self.client().post('/play',
                                 json={'quiz_category': 1,
                                       'previous_questions': None})
        self.assertEqual(res.status_code, 500)


"""
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
