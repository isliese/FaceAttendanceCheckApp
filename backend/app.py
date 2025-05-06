from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2, base64, numpy as np
from models import init_db, Student, Attendance
from face_service import load_database_embeddings, encode_face, recognize

# --- Setup ---
Session = init_db()  
app = Flask(__name__)
CORS(app)
db = Session()
known_names, known_embeds = load_database_embeddings(db)

# --- Endpoints ---
@app.route('/api/enroll', methods=['POST'])
def enroll():
    name = request.form['name']
    file = request.files['image']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    _, encs = encode_face(img)
    if not encs:
        return jsonify({'error':'No face detected'}), 400
    emb = ','.join(map(str, encs[0]))
    student = Student(name=name, embedding=emb)
    db.add(student); db.commit()
    return jsonify({'status':'enrolled', 'id':student.id})

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    data = request.json['image']  # data URI: 'data:image/png;base64,...'
    header, b64 = data.split(',',1)
    img_bytes = base64.b64decode(b64)
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    locs, encs = encode_face(img)
    names = recognize(encs, known_names, known_embeds)
    # log attendance
    responses = []
    for nm in names:
        if nm:
            student = db.query(Student).filter_by(name=nm).first()
            att = Attendance(student_id=student.id, present=True)
            db.add(att)
            responses.append({'name':nm, 'status':'present'})
        else:
            responses.append({'name':None, 'status':'not recognized'})
    db.commit()
    return jsonify(responses)

@app.route('/api/report', methods=['GET'])
def report():
    students = db.query(Student).all()
    report = []
    for s in students:
        was_present = db.query(Attendance)\
                       .filter_by(student_id=s.id, present=True)\
                       .count() > 0
        report.append({'name':s.name, 'present':was_present})
    return jsonify(report)

if __name__=='__main__':
    app.run(debug=True)