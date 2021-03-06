  # Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. 
The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. 
You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). 
This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for 
whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category 
and previous question parameters and return a random questions within the given category, 
if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## Endpoints
```
GET '/categories'
GET '/questions'
DELETE '/questions/<id>'
POST '/questions/add'
POST '/questions'
GET '/categories/<id>/questions'
POST '/play'
```
```
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
"categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }
}
Curl -X GET http://localhost:3000/categories

```
```
GET '/questions'
- Fetches a dictionary of questions in which categories are listed by type, total question are the count of all 
questions and questions contains all question with question attributes question:string,'answer:string,category:int,
difficulty:int
- Request Arguments: None
- Returns:
    categories: List of categories (string)  
    current_category: Current category for list of questions (string)
    total questions: Total questions
    questions: Dictionary with list of questions, for each question contains  
        "answer":  correct answer, string
        "category": question's category, string
        "difficulty": question's difficulty, int 
        "id": int: question's id, int
        "question": question to ask, string 

 
 "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "current_category": "", 
  "questions": [
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }, 
    {
      "answer": "Lake Victoria", 
      "category": 3, 
      "difficulty": 2, 
      "id": 13, 
      "question": "What is the largest lake in Africa?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": 3, 
      "difficulty": 3, 
      "id": 14, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }, 
    {
      "answer": "Agra", 
      "category": 3, 
      "difficulty": 2, 
      "id": 15, 
      "question": "The Taj Mahal is located in which Indian city?"
    }, 
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }
  ], 
  "total_questions": 178

% Curl -X GET http://localhost:3000/categories/1/questions

```
```
DELETE '/questions/<id>'
- Delete a question from Database using question id 
- Request Arguments: None
- Returns: Id of question deleted and success:True when it was deleted successfully.
 
{
  "id": "13", 
  "success": true
}

backend % curl -X DELETE -H "Content-Type: application/json"   http://localhost:3000/questions/12


```
```
POST '/questions/add'
- Persist a question using question string itself, answer string, category int, difficulty int.
- Request Arguments: question:string,'answer:string,category:int,difficulty:int
- Returns: Dictionary Object Success if the question added correctly 

{
  "answer": "Femur", 
  "category": 1, 
  "difficulty": 1, 
  "question": "Largest Bone in Humans", 
  "success": true
} 

 curl -X POST -H "Content-Type: application/json" -d '{"question":"Largest Bone in Humans","answer":"Femur",
"category":1,"difficulty":1}'  http://localhost:3000/questions/add
```
```
POST '/questions?searchTerm'
- Fetches a dictionary of questions in which the questions contains the searchTerm 
- Request Arguments: searchTerm: String
- Returns: An Object with questions that contains searchTerm on question attribute, total questions:int, 
current_cagegory:string and success True if fetches was made correctly.

{
  "current_category": "", 
  "questions": [
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "Match Go", 
      "category": 5, 
      "difficulty": 1, 
      "id": 25, 
      "question": "What is the name of Meteoro's Car"
    }
  ], 
  "success": true, 
  "total_questions": 6
}


curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"What"}'  http://localhost:3000/questions

```
```
GET '/categories/<id>/questions'
- Fetches a dictionary of questions by category.
- Request Arguments: category id : int
- Returns: A group of objests: 
 An object with categories, that contains a object of id: category_string key:value pairs.
An object with the list of questions that contains  answer, category, difficulty, question,id
Total of questions and succes if Fetche was made correctly.
{
  "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "currentCategory": "Science", 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "Femur", 
      "category": 1, 
      "difficulty": 1, 
      "id": 202, 
      "question": "Largest Bone in Humans"
    }
  ], 
  "success": true, 
  "totalQuestions": 4
}

Curl -X GET http://localhost:3000/categories/1/questions

```

```
POST '/play'
- Fetches a dictionary of a question matches with quiz_category and doesnt match with previos_question on request.
- Request Arguments: quiz_category, previous_questions
- Returns: 
An object with question that contains questions attributes, answer, category, difficlty, id, question,
success True if search was made it correctly.

{
  "question": {
    "answer": "The Liver", 
    "category": 1, 
    "difficulty": 4, 
    "id": 20, 
    "question": "What is the heaviest organ in the human body?"
  }, 
  "success": true
} 
 curl -X POST -H "Content-Type: application/json" -d '{"quiz_category":{"id":1,"type":"Science"},"previous_questions":[]}'  http://localhost:3000/play
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
