from flask import jsonify

def success_response(data=None, message="Success"):
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)

def error_response(message, status_code=400):
    return jsonify({
        'success': False,
        'message': str(message)
    }), status_code 