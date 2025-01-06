from flask import Blueprint, request
from app.utils.response import success_response, error_response
from app.models.user import User
from app.extensions import db
from app.utils.logger import logger

bp = Blueprint('user', __name__, url_prefix='/api/user')

@bp.route('/list', methods=['GET'])
def list_users():
    try:
        users = User.query.all()
        return success_response([user.to_dict() for user in users])
    except Exception as e:
        logger.exception("Error listing users")
        return error_response(str(e), 500)

@bp.route('/active', methods=['GET'])
def list_active_users():
    try:
        users = User.query.filter_by(status=True).all()
        return success_response([{
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname
        } for user in users])
    except Exception as e:
        logger.exception("Error listing active users")
        return error_response(str(e), 500)

@bp.route('/create', methods=['POST'])
def create_user():
    try:
        data = request.json
        username = data.get('username')
        nickname = data.get('nickname')
        cookie = data.get('cookie')
        
        if not all([username, cookie]):
            return error_response('Username and cookie are required')
            
        if User.query.filter_by(username=username).first():
            return error_response('Username already exists')
            
        user = User(
            username=username,
            nickname=nickname,
            cookie=cookie
        )
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(user.to_dict(), 'User created successfully')
    except Exception as e:
        logger.exception("Error creating user")
        return error_response(str(e), 500)

@bp.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found')
            
        data = request.json
        if 'username' in data:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return error_response('Username already exists')
            user.username = data['username']
            
        if 'nickname' in data:
            user.nickname = data['nickname']
        if 'cookie' in data:
            user.cookie = data['cookie']
        if 'status' in data:
            user.status = data['status']
            
        db.session.commit()
        return success_response(user.to_dict(), 'User updated successfully')
    except Exception as e:
        logger.exception("Error updating user")
        return error_response(str(e), 500)

@bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found')
            
        db.session.delete(user)
        db.session.commit()
        return success_response(message='User deleted successfully')
    except Exception as e:
        logger.exception("Error deleting user")
        return error_response(str(e), 500)

@bp.route('/<int:user_id>/cookie', methods=['GET'])
def get_user_cookie(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found')
        if not user.status:
            return error_response('User is inactive')
        return success_response({'cookie': user.cookie})
    except Exception as e:
        logger.exception("Error getting user cookie")
        return error_response(str(e), 500) 