import numpy as np
import face_recognition
from models import Student

def load_database_embeddings(db_session):
    """
    Load all student face embeddings from the database into memory.
    Returns a list of names and a list of corresponding embedding vectors.
    """
    students = db_session.query(Student).all()
    names, embeds = [], []
    for s in students:
        names.append(s.name)
        # Stored embedding is comma-delimited floats
        vec = np.fromstring(s.embedding, sep=',')
        embeds.append(vec)
    return names, embeds

def encode_face(image):
    """
    Given a BGR OpenCV image, detect all faces and return their locations
    and 128-dimensional encodings.
    """
    # Convert BGR (OpenCV) to RGB (face_recognition)
    rgb = image[:, :, ::-1]
    locs = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, locs)
    return locs, encs

def recognize(encodings, known_names, known_embeds, threshold=0.6):
    """
    Given a list of face encodings, compare each to the known embeddings.
    If the minimum distance is below `threshold`, return the matching name;
    otherwise return None.
    """
    results = []
    for enc in encodings:
        # Compute distances to all known embeddings
        dists = face_recognition.face_distance(known_embeds, enc)
        best = np.argmin(dists)
        if dists[best] < threshold:
            results.append(known_names[best])
        else:
            results.append(None)
    return results