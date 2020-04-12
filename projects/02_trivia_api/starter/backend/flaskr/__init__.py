import os

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import exc
import random


from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    # initializing CORS with default options
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/categories')
    @cross_origin()
    def get_categories():
        data = request.get_json()
        if data:
            raise InvalidUsage('Extra arguments doesnt needed.',status_code=400)
        formatted_categories = {}
        all_categories = Category.query.all()
        for c in all_categories:
            if c.id not in formatted_categories.keys():
                formatted_categories[c.id] = c.type
        return jsonify({
            'categories': formatted_categories
        })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    def paginate_questions(request, selection):

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route('/questions', methods=['GET'])
    @cross_origin()
    def get_questions():
        data = request.get_json()
        if data:
            raise InvalidUsage('Extra arguments doesnt needed.', status_code=400)

        all_questions = Question.query.all()
        questions = paginate_questions(request, all_questions)
        all_categories = Category.query.all()
        formatted_categories = ['{}'.format(category.type) for category in all_categories]

        return jsonify({
            'total_questions': len(all_questions),
            'questions': questions,
            'categories': formatted_categories,
            'current_category': '',

        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route('/questions/<id>', methods=['DELETE'])
    @cross_origin()
    def delete_question(id):
        success = False
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if not question:
                raise InvalidUsage('Id doesnt exist', status_code=422)
            db.session.delete(question)
            db.session.commit()

        except exc.SQLAlchemyError:
            db.session.rollback()
        else:
            success = True
        return jsonify(
            {'success': success,
             'id':id}
        )

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.route('/questions/add', methods=['POST'])
    @cross_origin()
    def summit_question():
        formq = request.get_json()
        if not formq:
            raise InvalidUsage('Args needed.',status_code=400)

        for elem in formq.keys():
            if elem not in {'question','answer','category','difficulty'}:
                raise InvalidUsage('Extra args doesnt needed.',status_code=422)

        question = formq['question']
        answer = formq['answer']
        category = formq['category']
        difficulty = formq['difficulty']
        if question=='' or answer=='':
            raise InvalidUsage('Args should be empty.',status_code=422)
        q_obj = Question(question=question, answer=answer,
                         difficulty=difficulty, category=category)
        try:
            db.session.add(q_obj)
            db.session.commit()

        except exc.SQLAlchemyError:
            db.session.rollback()
            success = False
        else:
            success = True
        return jsonify({'success': success,
                        'question': question,
                        'answer': answer,
                        'category': category,
                        'difficulty': difficulty
                        })

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def summit_search():
        success = True
        d = request.get_json()
        if d and 'searchTerm' in d:
            search = '%{}%'.format(d['searchTerm'])
            all_questions = Question.query.filter(Question.question.ilike(search)).all()
        else:
            all_questions = Question.query.all()

        questions = paginate_questions(request, all_questions)

        return jsonify({'success': success,
                        'total_questions': len(all_questions),
                        'questions': questions,
                        'current_category': '',
                        })

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<id>/questions', methods=['GET'])
    @cross_origin()
    def get_by_category(id):
        try:
            success = True
            params = request.get_json()
            if params:
                raise InvalidUsage('Extra attributes not required.',status_code=422)
            cat = Category.query.get(id)
            if not cat:
                raise InvalidUsage('Category Doesnt Exist',status_code=422)
            all_questions = Question.query.filter(Question.category == id).all()
            questions = paginate_questions(request, all_questions)
            all_categories = Category.query.all()
            formatted_categories = ['{}'.format(category.type) for category in all_categories]
        except exc.SQLAlchemyError:
            success = False
        return jsonify({'success': success,
                        'totalQuestions': len(all_questions),
                        'questions': questions,
                        'categories': formatted_categories,
                        'currentCategory': cat.type,
                        })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/play', methods=['POST'])
    @cross_origin()
    def get_next_question():
        success = True

        params = request.get_json()
        quiz_category = params['quiz_category']
        previous_questions = params['previous_questions']

        if quiz_category['type'] == 'click':
            question = Question.query.filter(~Question.id.in_(previous_questions)).first()
        else:
            cat = Category.query.filter(Category.id == quiz_category['id']).subquery()
            question = Question.query.join(cat, cat.c.id == Question.category). \
                filter(~Question.id.in_(previous_questions)).first()

        return jsonify({'success': success,
                        'question': {'id': question.id, 'answer': question.answer,
                                     'difficulty': question.difficulty,
                                     'question': question.question,
                                     'category': question.category}}
                       )
    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    class InvalidUsage(Exception):
        status_code = 0

        def __init__(self, message, status_code=None, payload=None):
            Exception.__init__(self)
            self.message = message
            if status_code is not None:
                self.status_code = status_code
            self.payload = payload

        def to_dict(self):
            rv = dict(self.payload or ())
            rv['message'] = self.message
            rv['status_code'] = self.status_code
            return rv

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    return app
