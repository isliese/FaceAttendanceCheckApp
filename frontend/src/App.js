import React, { useRef, useState, useEffect } from 'react';

export default function App() {
  const videoRef = useRef();
  const [report, setReport] = useState([]);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => videoRef.current.srcObject = stream);
  }, []);

  const captureAndSend = async () => {
    const canvas = document.createElement('canvas');
    const v = videoRef.current;
    canvas.width = v.videoWidth; canvas.height = v.videoHeight;
    canvas.getContext('2d').drawImage(v, 0, 0);
    const data = canvas.toDataURL('image/png');
    const res = await fetch('http://localhost:5000/api/recognize', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ image: data })
    });
    const json = await res.json();
    console.log(json);
  };

  const fetchReport = async () => {
    const res = await fetch('http://localhost:5000/api/report');
    setReport(await res.json());
  };

  return (
    <div className="p-4">
      <h1 className="text-xl mb-2">FaceAttend</h1>
      <video ref={videoRef} autoPlay width={640} height={480} className="border" />
      <div className="mt-2">
        <button onClick={captureAndSend} className="mr-2 p-2 bg-blue-500 text-white rounded">
          Scan Now
        </button>
        <button onClick={fetchReport} className="p-2 bg-green-500 text-white rounded">
          Show Attendance
        </button>
      </div>
      <ul className="mt-4">
        {report.map(r => (
          <li key={r.name} className={r.present ? 'text-green-600' : 'text-red-600'}>
            {r.name}: {r.present ? 'Present' : 'Absent'}
          </li>
        ))}
      </ul>
    </div>
  );
}