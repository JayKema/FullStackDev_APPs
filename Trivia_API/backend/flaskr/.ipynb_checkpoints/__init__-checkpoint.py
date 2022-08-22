from operator import not_
import os
#from types import NoneType
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted = [cat.format() for cat in categories]
        return jsonify(
            {
                "success":True,
                "total_categories": len(formatted),
                "categories":{cat['id']:cat['type'] for cat in formatted}
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')
        start = (page - 1) * QUESTIONS_PER_PAGE
        end  = start + QUESTIONS_PER_PAGE

        query = Question.query.all()
        formatted = [question.format() for question in query]
        questions = formatted[start:end]
        
        if questions==[]:
            abort(400)
        
        return jsonify(
            {
                'questions': questions,
                'total_questions':len(formatted),
                'current_category': category,
                'categories': {cat.id:cat.type for cat in Category.query.all()},
                'success':True
            }
        )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id): 
        error=False
        print(id)
        try:  
            question = Question.query.filter(Question.id==id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
        except:
            error=True
        finally:
            if error==True:
                abort(404)
            
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.order_by('id').all()
            formatted = [question.format() for question in questions]
            subset = formatted[start:end]
            return jsonify(
                {
                    'current_questions':subset,
                    'total_questions': len(questions),
                    'success':True
                }
            )

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_questions():
        data = request.get_json()
        
        error=False
        try:
            new_question =  Question(question = data.get('question'), 
                                answer = data.get('answer'), 
                                category = data.get('category'), 
                                difficulty = data.get('difficulty'))
            id = new_question.id
            new_question.insert()
        except:
            error = True
        
        finally:
            if error==True:
                abort(500)
            else:
                question = Question.query.filter(Question.id==id).all()
                return jsonify(success=True)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search_questions():
        search_term = request.get_json().get('searchTerm')
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')
        categories = {cat.id:cat.type for cat in Category.query.all()}
        start = (page - 1) * QUESTIONS_PER_PAGE
        end  = start + QUESTIONS_PER_PAGE

        error = False
        try:   
            query = Question.query.order_by('id').filter(Question.question.ilike(f'%{search_term}%')).all()
            format_questions = [question.format() for question in query]
            questions = format_questions[start:end]
            print(query)
            if query == []:
                abort(404)
        except:
                questions = []
                error = True
        finally:
            if error == True:
                return jsonify(
                        {
                            'questions': questions,
                            'total_questions':len(questions),
                            'current_category': category,
                            'categories': {cat:categories[cat] for cat in set(categories).intersection([cat_id['category'] for cat_id in questions])}
                        }
                    ),abort(404, description="resource not foundS")
            else:
                return jsonify(
                        {
                            'questions': questions,
                            'total_questions':len(questions),
                            'current_category': category,
                            'categories': {cat:categories[cat] for cat in set(categories).intersection([cat_id['category'] for cat_id in questions])},
                        'success': True}
                    )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<id>/questions', methods=['GET'])
    def get_categories_questions(id):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end  = start + QUESTIONS_PER_PAGE

        query = Question.query.filter(Question.category==id).all()
        formatted = [question.format() for question in query]
        questions = formatted[start:end]
        
        if questions==[]:
            abort(404)
        
        return jsonify(
            {
                'questions': questions,
                'total_questions':len(formatted),
                'current_category': id,
                'categories': {cat.id:cat.type for cat in Category.query.all()},
                'success': True
            }
        )


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        res = request.get_json()
        category = res.get('quiz_category').get('id')
        previous_questions = res.get('previous_questions')

        if category == 0:
            query = Question.query.filter(Question.id.notin_(previous_questions)).all()
        elif Category.query.filter_by(id=int(category)).all()==[]:
            abort(404)
        else:
            query = Question.query.filter(Question.category==category).filter(Question.id.notin_(previous_questions)).all()
        print(query)
        if not len(query)>0:
            return jsonify({})
        else:
            questions = [question.format() for question in query]
            choice = random.choices(questions, k=1)
            return jsonify(question=choice[0], success=True)







    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                'success': False,
                'message': "resource not found",
                'error': 404
            }
        ),404
    
    @app.errorhandler(422)
    def unprocessed_request(error):
        return jsonify(
            {
                'success': False,
                'message': "unprocessable request",
                'error': 422
            }
        ),422
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify(
            {
                'success': False,
                'message': "internal server error",
                'error': 500
            }
        ),500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                'success': False,
                'message': "bad request",
                'error': 400
            }
        ),400
    
    @app.errorhandler(405)
    def method_unallowed(error):
        return jsonify(
            {
                'success': False,
                'message': "method not allowed",
                'error': 405
            }
        ),405



    return app
