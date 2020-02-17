import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [q.format() for q in selection]
    current_questions = formatted_questions[start:end]
    return current_questions


def __get_categories():
    all_categories = Category.query.order_by(Category.id).all()
    categories = {}
    for category in all_categories:
        categories[category.id] = category.type
    return categories


def __get_questions_by_category(category_id):
    if category_id == '':
        abort(400)

    if category_id != 0:
        questions = Question.query.filter
        (Question.category == category_id).all()
    else:
        questions = Question.query.all()

    if not questions:
        abort(400)

    return [q.format() for q in questions]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app)
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization,true'
            )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE,OPTIONS'
            )
        return response
    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = __get_categories()
        print(len(categories))
        if len(categories) == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'categories': categories
              })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate(request, selection)
        if len(current_questions) == 0:
            abort(404)

        categories = __get_categories()
        # length = len(current_questions)
        # current_category = []
        # for i in range(length):
        #     current_category.append(current_questions[i]["category"])
        #     print(current_category)
        #     for q in current_questions:
        #         if q['category'] == current_category[i]:
        #             q['current_category'] = current_category

        return jsonify({
            'success': True,
            'current_questions': current_questions,
            'total_questions': len(selection),
            # 'current_category': current_category,
            'categories': categories
        })

    # @app.route('/questions', methods=['GET'])
    # def get_questions():
    #     selection = Question.query.order_by(Question.id).all()
    #     current_questions = paginate(request, selection)
    #     categories_data = Category.query.all()
    #     categories = []

    #     for category in categories_data:
    #         categories.append(category.type)

    #     if len(current_questions) == 0:
    #         abort(404)

    #     return jsonify({
    #         'success': True,
    #         'questions': current_questions,
    #         'total_questions': len(selection),
    #         'current_category': None,
    #         'categories': categories
    #     })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.all()
            current_questions = paginate(request, selection)

            return jsonify({
              'success': True,
              'deleted_question': question.id,
              'current_questions': current_questions,
              'total_questions': len(selection)
            })
        except:
            abort(422)

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will
    appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('search', None)

        try:
            if search is not None:
                selection = Question.query.filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate(request, selection)

                return jsonify({
                    'success': True,
                    'search_questions': current_questions,
                    'total_questions': len(selection.all())
                })

            else:
                if not new_question or not new_answer or not new_category or not new_difficulty:
                    abort(400)

                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty
                    )

                question.insert()

                selection = Question.query.all()
                current_questions = paginate(request, selection)

                return jsonify({
                    'success': True,
                    'current_questions': current_questions,
                    'total_questions': len(selection)
                    })
        except:
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    # @app.route('/questions', methods=['POST'])
    # def search_result():
    #     body = request.get_json()
    #     search = body.get('search', None)

    #     try:
    #         if search is not None:
    #             if body['search'] == '':
    #                 abort(400)

    #             selection = Question.query.filter(Question.question.ilike('%{}%'.format(search)))
    #             search_result = paginate(request, selection)

    #             return jsonify({
    #                 'success': True,
    #                 'search_result': search_result,
    #                 'total_questions': len(selection.all())
    #             })
    #     except:
    #         abort(422)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_based_on_category(category_id):
        try:
            category = Category.query.filter(Category.id == category_id).one_or_none()
            if not category:
                abort(400)

            selection = Question.query.filter(Question.category == category_id).all()
            if not selection:
                abort(404)

            current_questions = paginate(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': category.type
            })
        except:
            abort(400)

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

    @app.route('/quizzes', methods=['POST'])
    def play_trivia():
        body = request.get_json()
        # quiz_category = body.get('quiz_category')
        # category_id = quiz_category.get('id', None)
        category_id = body.get('id', None)
        previous_questions = body.get('pervious_questions', [])

        questions = __get_questions_by_category(category_id)
        if len(questions) == 0:
            abort(404)
        current_question = random.choice(questions)
        keep_playing = True

        try:
            while keep_playing:
                if current_question.get('id') not in previous_questions:
                    print('plaplapla')
                    return jsonify({
                            "success": True,
                            "status_code": 200,
                            "status_message": "OK",
                            "question": current_question
                        })
                else:
                    if len(questions) > len(previous_questions):
                        current_question = random.choice(questions)
                    else:
                        keep_playing = False

            return jsonify({
                    "success": True,
                    "status_code": 200,
                    "status_message": "OK",
                    "question": current_question
            })

        except:
            abort(400)

        # if len(questions) > 0:
        #     question = random.choice(questions)
        #     return jsonify({
        #         'success': True,
        #         'question': question
        #     })
        # else:
        #     abort(404)

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(404)
    def not_founf(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def not_founf(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
