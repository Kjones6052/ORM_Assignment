# Importing as needed
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError


# Instantiating Flask App
app = Flask(__name__)

# Configure SQLAlchemy to connect to database using connection parameteres
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:7Raffi!Codes7@localhost/fitness_center_db'

# Enable app to use SQLAlchemy and Marshmallow
db = SQLAlchemy(app) # Gives full access to SQL database functionality
ma = Marshmallow(app) # Gives access to data parsing and validation

# Class schema for Members
class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True) 
    age = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

# Class schema for Workout Sessions
class WorkoutSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True) 
    session_date = fields.Date(required=True)
    session_time = fields.Time(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("session id", "member id", "session date", "session time", "activity")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

# Class Model for Members
class Member(db.Model):
    __tablename__ = "Members" # Defining table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    workout_sessions = db.relationship('WorkoutSession', backref='member')

# Class Model for Workout Sessions
class WorkoutSession(db.Model):
    __tablename__ = "WorkoutSessions" # Defining table name
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    activity = db.Column(db.String, nullable=False)
    member = db.relationship('Member', backref='workoutsession')

# Route and method to Add New Member using POST
@app.route("/members", methods=["POST"])
def new_member():
    try:
        member_data = member_schema.load(request.json) # Validate and deserialize input
    except ValidationError as err: # Error handling
        return jsonify(err.messages), 400 # Jsonify error with type indicator
    
    # Adding customer info into a variable for query execution
    new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
    db.session.add(new_member) # Execute query to add new member
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "New Member added successfully."}), 201
    
# Route and method to Update a Member using PUT
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    member = Member.query.get_or_404(id) # Retrieve Member by Member ID or produce 404 if not found
    try:
        member_data = member_schema.load(request.json) # Validate and deserialize input
    except ValidationError as err: # Error handling
        return jsonify(err.messages), 400 # Jsonify error with type indicator
    
    # Defining member data
    member.id = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "Member was updated successfully."}), 200

# Route and method to View All Members using GET
@app.route("/members", methods=["GET"])
def get_all_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

# Route and method to View a Member using GET
@app.route("/members/<int:id>", methods=["GET"])
def get_member(id):
    member = Member.query.get_or_404(id)
    return member_schema.jsonify(member)

# Route and method to Delete a Member using DELETE
@app.route("/members/<int:id>", methods=["DELETE"])
def remove_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member was successfully removed."}), 200

# Route and method to Add New Workout Session using POST
@app.route("/workoutsessions", methods=["POST"])
def new_workout_session():
    try:
        workout_data = workout_schema.load(request.json) # Validate and deserialize input
    except ValidationError as err: # Error handling
        return jsonify(err.messages), 400 # Jsonify error with type indicator
    
    # Adding workout session info into a variable for query execution
    new_workout = WorkoutSession(session_id=workout_data['session id'], member_id=workout_data['member id'], session_date=workout_data['session date'], session_time=workout_data['session time'], activity=workout_data['activity'])
    db.session.add(new_workout) # Execute query to add new workout session
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "New workout session was scheduled successfully."}), 201

# Route and method to Update a Workout Session using PUT
@app.route("/workoutsessions/<int:session_id>/<int:member_id>", methods=["PUT"])
def update_workout(session_id, member_id):
    workout = WorkoutSession.query.get_or_404(session_id, member_id) # Retrieve Workout Session by Session ID and Member ID or produce 404 if not found
    try:
        workout_data = workout_schema.load(request.json) # Validate and deserialize input
    except ValidationError as err: # Error handling
        return jsonify(err.messages), 400 # Jsonify error with type indicator
    
    # Defining member data
    workout.session_id = workout_data['session id']
    workout.member_id = workout_data['member id']
    workout.session_date = workout_data['session date']
    workout.session_time = workout_data['session time']
    workout.activity = workout_data['activity']
    db.session.commit() # Commit changes to the database
    return jsonify({"message": "Workout session was updated successfully."}), 200

# Route and method to View All Workout Sessions using GET
@app.route("/workoutsessions", methods=["GET"])
def get_all_workouts():
    workouts = WorkoutSession.query.all() # Retrieve All Workout Sessions
    return workouts_schema.jsonify(workouts)

# Route and method to View a Workout Session using GET
@app.route("/workoutsessions/<int:session_id>/<int:member_id>", methods=["GET"])
def get_workout(session_id, member_id):
    workout = WorkoutSession.query.get_or_404(session_id, member_id) # Retrieve Workout Session by Session ID and Member ID or produce 404 if not found
    return workout_schema.jsonify(workout)

# Route and method to Delete a Workout Session using DELETE
@app.route("/workoutsessions/<int:session_id>/<int:member_id>", methods=['DELETE'])
def delete_workout(session_id, member_id):
    workout = WorkoutSession.query.get_or_404(session_id, member_id) # Retrieve Workout Session by Session ID and Member ID or produce 404 if not found
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout session was successfully removed."}), 200

