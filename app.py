from flask import Flask,request,jsonify
import firebase_admin
from firebase_admin import credentials, firestore,auth
#create flask application
app = Flask(__name__)
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
from functools import wraps

def verify_token(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Authorization token is missing"
            }), 401

        try:
            token = auth_header.split("Bearer ")[1]

            decoded_token = auth.verify_id_token(token)

            request.user = decoded_token

        except Exception as e:
            return jsonify({
                "error": "Invalid Token",
                "details": str(e)
            }), 401

        return f(*args, **kwargs)

    return decorated   
#Home route 
@app.route("/")
def home():
    return  "Firebase is connected successfully "
#POST API
@app.route("/students", methods=["POST"])
@verify_token
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data found"
        }), 400

    doc_ref = db.collection("students").document()
    doc_ref.set(data)

    return jsonify({
        "message": "Student added successfully",
        "document_id": doc_ref.id,
        "student": data
    }), 201
@app.route("/students", methods=["GET"])
@verify_token
def get_students():
    docs = db.collection("students").stream()
    students = []
    for doc in docs:
         student = doc.to_dict()
         student["id"] = doc.id
         students.append(student)
    return jsonify(students), 200

@app.route("/students/<student_id>", methods=["GET"])
@verify_token

def get_student_by_id(student_id):
    doc = db.collection("students").document(student_id).get()

    if not doc.exists:
        return jsonify({
            "error" : "Student not found"
        }),404

    student = doc.to_dict()
    student["id"] = doc.id
    return jsonify(student), 200

@app.route("/students/<student_id>", methods=["PUT"])
@verify_token

def update_student(student_id):
    data = request.get_json()
    if not data:
        return jsonify({
            "error" : "No data found"
        }),400
    doc_ref = db.collection("students").document(student_id)
    if not doc_ref.get().exists :
        return jsonify({
            "error" : "student not found"
        }),404
    doc_ref.update(data)
    return jsonify({
        "message" : "Student updated successfully",
        "student_id": student_id,
        "updated_data" : data
    }),200
@app.route("/students/<student_id>", methods=["DELETE"])
@verify_token

def delete_student(student_id):

    doc_ref = db.collection("students").document(student_id)

    if not doc_ref.get().exists:
        return jsonify({
            "error": "Student not found"
        }), 404

    doc_ref.delete()

    return jsonify({
        "message": "Student deleted successfully",
        "student_id": student_id
    }), 200
 
#start the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
   
   



