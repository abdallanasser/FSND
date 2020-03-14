import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
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
def get_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0:
        print('no drinks')
        abort(404)

    drinks_short_form = []
    for drink in drinks:
        drink = drink.short()
        drinks_short_form.append(drink)
    
    return jsonify({
        "success": True, "drinks": drinks_short_form
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth(permission='get:drinks_detail')
def get_drink_detail(payload):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)
    
    drinks_long_form = []
    for drink in drinks:
        drink = drink.long()
        drinks_long_form.append(drink)

    return jsonify({
        "success": True, "drinks": drinks_long_form
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

@app.route('/drinks', methods=["POST"])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = json.dumps(body.get('recipe', None))

    if not title or not recipe:
        abort(422)

    drink = Drink.query.filter(Drink.title == title).one_or_none()

    if drink:
        abort(409)

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({
            "success": True, "drinks": drink.long()
        })
    except Exception:
        abort(422)

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

@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth(permission='patch:drinks')
def patch_drinks_details(payload, id):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = json.dumps(body.get('recipe', None))

        if not title or not recipe:
            abort(422)

        drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        if not drink:
            abort(400)

        drink.title = title
        drink.recipe = recipe
        drink.update()

        return jsonify({
            "success": True, "drinks": drink.long()
        })
    except Exception:
        abort(422)

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

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        if not drink:
            abort(400)

        drink.delete()

        return jsonify({
            "success": True, "delete": id
        })
    except Exception:
        abort(422)

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

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405, 
        "message": "not allowed"
    }), 405


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "conflicts with some rule already established"
    }), 409


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "not authorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(AuthError)
def authorize_authenticate_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code


'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
