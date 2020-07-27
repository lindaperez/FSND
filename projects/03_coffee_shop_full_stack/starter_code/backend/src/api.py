import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


# db_drop_and_create_all()

## Utility

def get_db_drinks(param):
    drinks = []
    try:
        db_drinks = Drink.query.all()
    except exc.SQLAlchemyError:
        success = False
    else:
        if param == 'long':
            for d in db_drinks:
                drinks.append(Drink(id=d.id, title=d.title, recipe=d.recipe).long())
        elif param == 'short':
            for d in db_drinks:
                drinks.append(Drink(id=d.id, title=d.title, recipe=d.recipe).short())
        success = True
    return success, drinks


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
@cross_origin()
def get_drinks():
    success, drinks = get_db_drinks('short')

    return jsonify({
        'success': success,
        'drinks': drinks,
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@cross_origin()
@requires_auth('get:drinks-detail')
def get_drinks_detail(args):
    success, drinks = get_db_drinks('long')

    return jsonify({
        'success': success,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@cross_origin()
@requires_auth('post:drinks')
def post_drink(arg):
    form = request.get_json()
    title = form['title']
    recipe = form['recipe']
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drinks = []
    try:
        drink.insert()
    except exc.SQLAlchemyError:
        db.session.rollback()
        success = False
    else:
        success, drinks = get_db_drinks('long')
    return jsonify({'success': success,
                    'drinks': drinks
                    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@cross_origin()
@requires_auth('patch:drinks')
def patch_drink(args, id):
    drinks = []
    try:
        d = Drink.query.filter(Drink.id == id).one_or_none()
        if not d:
            raise ExcHandling('Id doesnt Exist.', status_code=400)
        form = request.get_json()
        d.title = form['title']
        d.recipe = json.dumps(form['recipe'])
        d.update()
        success, drinks = get_db_drinks('long')

    except exc.SQLAlchemyError:

        db.session.rollback()
        success = False

    return jsonify({'success': success,
                    'drinks': drinks
                    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@cross_origin()
@requires_auth('delete:drinks')
def delete_drink(arg, id):
    drinks = []
    try:
        d = Drink.query.filter(Drink.id == id).one_or_none()
        if not d:
            raise ExcHandling('Id doesnt Exist.', status_code=400)
        d.delete()
        success, drinks = get_db_drinks('long')

    except exc.SQLAlchemyError:

        db.session.rollback()
        success = False

    return jsonify({'success': success,
                    'drinks': drinks
                    })


## Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

class ExcHandling(Exception):
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


@app.errorhandler(ExcHandling)
def exc_handling(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


'''

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "401 Unauthorized. Required authentication"
    }), 401
'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

'''
@app.errorhandler(404)
def notFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
'''

@app.errorhandler(403)
def authError(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Authentication Error"
    }), 403

'''