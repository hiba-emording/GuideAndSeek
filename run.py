#!/usr/bin/python3
""" Entry Point"""
from app import socketio, create_app


app = create_app()


if __name__ == '__main__':
    socketio.run(app, debug=True)
