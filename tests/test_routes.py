from flask import Flask, jsonify
import pytest

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Flask Terminal Project' in response.data

def test_terminal(client):
    response = client.get('/terminal')
    assert response.status_code == 200
    assert b'Terminal Interface' in response.data

def test_execute_command(client):
    response = client.post('/execute_command', json={'command': 'ls'})
    assert response.status_code == 200
    assert 'output' in response.get_json()