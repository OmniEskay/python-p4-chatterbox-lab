#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    """Get all messages ordered by created_at in ascending order"""
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages])

@app.route('/messages', methods=['POST'])
def create_message():
    """Create a new message"""
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate required fields
        if not data or 'body' not in data or 'username' not in data:
            return jsonify({'error': 'Both body and username are required'}), 400
        
        # Create new message
        new_message = Message(
            body=data['body'],
            username=data['username']
        )
        
        # Add to database
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify(new_message.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    """Update a message's body"""
    try:
        # Find the message
        message = Message.query.get(id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Get data from request
        data = request.get_json()
        
        # Validate required field
        if not data or 'body' not in data:
            return jsonify({'error': 'Body is required'}), 400
        
        # Update the message
        message.body = data['body']
        db.session.commit()
        
        return jsonify(message.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    """Delete a message"""
    try:
        # Find the message
        message = Message.query.get(id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Delete the message
        db.session.delete(message)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)