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

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], '')
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_verify_pagination(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], '')
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        if data['total_questions'] > 10:
            self.assertEqual(len(data['questions']), 10)
    """
    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 2).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)    
        
    """
    def test_add_question(self):
        res = self.client().post('/questions/add',
                                 json={'question': 'Men who put first foot at the moon',
                                       'answer': 'Neil Amstrong', 'category': 4, 'difficulty': 4})

        self.assertEqual(res.status_code, 200)

    # HTTP REQUEST ERRORS
    def test_verify_404_categories(self):
        res = self.client().get('/categori')
        self.assertEqual(res.status_code, 404)

    def test_verify_400_categories(self):
        res = self.client().get('/categories', json={'cat': 1})
        self.assertEqual(res.status_code, 400)

    def test_verify_404_questions(self):
        res = self.client().get('/questio')
        self.assertEqual(res.status_code, 404)

    def test_verify_400_questions(self):
        res = self.client().get('/questions', json={'quest': 1})
        self.assertEqual(res.status_code, 400)

    def test_verify_404_delete_question_by_id(self):
        res = self.client().delete('/questio/1')
        self.assertEqual(res.status_code, 404)

    def test_verify_422_delete_question_by_id(self):
        res = self.client().delete('/questions/1')
        self.assertEqual(res.status_code, 422)

    """
    def test_verify_422_delete_question_by_id(self):
        #
        res = self.client().get('/questions/1', json={'method': 'DELETE'})
        self.assertEqual(res.status_code, 422)
    """

    def test_verify_404_question_by_category(self):
        res = self.client().get('/categories/1/quesons')
        self.assertEqual(res.status_code, 404)

    def test_verify_422_question_by_category(self):
        res = self.client().get('/categories/10/questions', json={'cat': 1})
        self.assertEqual(res.status_code, 422)

    def test_verify_404_add_question(self):
        res = self.client().post('/add')
        self.assertEqual(res.status_code, 404)

    def test_verify_422_add_question(self):
        res = self.client().post('/questions/add',
                                 json={'question': 'Men who put first foot at the moon',
                                       'answer': 'Neil Amstrong', 'category': 4, 'difficulty': 4, 'cat': 5})
        self.assertEqual(res.status_code, 422)

    def test_verify_400_add_question(self):
        res = self.client().post('/questions/add')
        self.assertEqual(res.status_code, 400)


"""
"""

"""
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
