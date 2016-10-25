#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Ji Hwan Kim
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
'''
additional import: redirect, jsonify
redirect for redirecting url, jsonify for passing dict object from server to client
'''

from flask import Flask, request, redirect, jsonify
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    # set some 
    def set(self, entity, data):
        self.space[entity] = data

    # clear seems to be clearing the world
    def clear(self):
        self.space = dict()

    # need to use this get to get entities from server then pass it to client
    def get(self, entity):
        return self.space.get(entity,dict())

    # this only returns world excluding entities.
    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: appication/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data != ''):
        return json.loads(request.data)
    else:
        return json.loads(request.form.keys()[0])

'''
Note to self.
It is very important that I should return json object to client once
I modify the World object, if I do not return new json with modified World,
the client will not acknowledge the changes made.
Also retrieve json from client using flask_post_json method.
'''

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect("/static/index.html", code = 302)

# we dont return myWorld.world() here since we only using entity
# so we need to get entity then return that to json
@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    client_json = flask_post_json()
    if request.method == 'POST':
        # if method is POST, then we set the entity
        myWorld.set(entity, client_json)
        # now need to get the entities from world
        ent = myWorld.get(entity)
        return flask.jsonify(**ent)

    elif request.method == 'PUT':
        # if method is PUT, then we update the entity
        for key in client_json.keys():
            myWorld.update(entity, key, client_json[key])
        # now need to get the entities from world
        ent = myWorld.get(entity)
        return flask.jsonify(**ent)

# we can return myWorld here since no entities were modified
@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    if request.method == 'POST':
        # if method is POST, then we set the world, but entity not given...
        client_json = flask_post_json()
        myWorld.set(client_json)
        return flask.jsonify(myWorld.world())
    elif request.method == 'GET':
        # if method is GET, then we return the world
        return flask.jsonify(myWorld.world())

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    # we read the entity
    ent = myWorld.get(entity)
    return flask.jsonify(**ent)

# we can return myWorlds here since no entities were modified
@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    if request.method == 'POST':
        myWorld.clear()
        return flask.jsonify(myWorld.world())

    elif request.method == 'GET':
        myWorld.clear()
        return flask.jsonify(myWorld.world())

if __name__ == "__main__":
    app.run()
