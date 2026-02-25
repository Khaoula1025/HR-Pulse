"use client";
import React, { useState } from 'react';
import axios from 'axios';
import { Calculator, Sparkles, Plus, X } from 'lucide-react';

export default function PredictorPage() {
  const [jobTitle, setJobTitle] = useState('');
  const [currentSkill, setCurrentSkill] = useState('');
  const [skills, setSkills] = useState<string[]>([]);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const addSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (currentSkill && !skills.includes(currentSkill)) {
      setSkills([...skills, currentSkill]);
      setCurrentSkill('');
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter(s => s !== skillToRemove));
  };

  const handlePredict = async () => {
    setLoading(true);
    try {
      // Ensure this URL matches your FastAPI server address
      const response = await axios.post('http://127.0.0.1:8000/app/api/v1/endpoints/predictor', {
        job_title: jobTitle,
        skills: skills
      });
      setPrediction(response.data.estimated_salary);
    } catch (error) {
      console.error("Prediction failed", error);
      alert("Failed to get prediction. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Salary Predictor</h1>
        <p className="text-gray-600">Enter your details to see your estimated market value.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Job Title</label>
            <input 
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g. Data Scientist"
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Skills</label>
            <form onSubmit={addSkill} className="flex gap-2 mb-3">
              <input 
                type="text"
                value={currentSkill}
                onChange={(e) => setCurrentSkill(e.target.value)}
                placeholder="Add a skill (e.g. Python)"
                className="flex-1 px-4 py-2 border border-gray-200 rounded-lg outline-none"
              />
              <button type="submit" className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700">
                <Plus size={20} />
              </button>
            </form>
            
            <div className="flex flex-wrap gap-2">
              {skills.map(skill => (
                <span key={skill} className="flex items-center gap-1 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                  {skill}
                  <button onClick={() => removeSkill(skill)}><X size={14}/></button>
                </span>
              ))}
            </div>
          </div>

          <button 
            onClick={handlePredict}
            disabled={loading || !jobTitle}
            className="w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-indigo-700 disabled:bg-gray-300 transition-colors"
          >
            {loading ? "Calculating..." : <><Calculator size={20}/> Predict Salary</>}
          </button>
        </div>

        {/* Result Section */}
        <div className="bg-indigo-900 rounded-2xl p-8 text-white flex flex-col justify-center items-center text-center">
          {!prediction ? (
            <>
              <Sparkles size={48} className="text-indigo-300 mb-4 animate-pulse" />
              <p className="text-indigo-200">Enter your details and click predict to see the magic happen.</p>
            </>
          ) : (
            <div className="animate-in fade-in zoom-in duration-500">
              <h2 className="text-indigo-300 uppercase tracking-widest text-sm font-bold mb-2">Estimated Annual Salary</h2>
              <div className="text-6xl font-extrabold mb-4">
                ${prediction.toLocaleString()}
              </div>
              <p className="text-indigo-200 text-sm">
                Based on your profile and current market trends in our dataset.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}