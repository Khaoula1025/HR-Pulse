"use client";
import { useState, useEffect } from "react";

export default function Predict() {
  const [skillsList, setSkillsList] = useState<string[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    company_name: "",
    job_title: "",
    location: "",
    skills: [] as string[],
    rating: 3.5,
    founded: 2000,
    size_ordinal: 3, // e.g., 501 to 1000 employees
    revenue_ordinal: 2, // e.g., $100 to $500 million
    type_of_ownership: "Private Practice / Firm",
    has_competitors: false,
    job_state: "NY",
    sector: "Information Technology",
    seniority: "na",
    core_role: "data scientist"
  });

  useEffect(() => {
    // Fetch valid skills from your predictor endpoint
    fetch("/api/predict/skills")
      .then((res) => res.json())
      .then((data) => setSkillsList(data.skills));
  }, []);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("/api/predict", { // Hits router.post("") in predictor.py
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.[0]?.msg || "Prediction failed");
      setResult(data);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleSkill = (skill: string) => {
    setForm(prev => ({
      ...prev,
      skills: prev.skills.includes(skill) 
        ? prev.skills.filter(s => s !== skill) 
        : [...prev.skills, skill]
    }));
  };

  return (
    <div className="p-6 bg-slate-900 min-h-screen text-slate-200">
      <h1 className="text-3xl font-bold mb-8 text-indigo-400">Salary Estimator</h1>
      
      <div className="grid lg:grid-cols-3 gap-8">
        {/* FORM SECTION */}
        <form onSubmit={handlePredict} className="lg:col-span-2 space-y-6 bg-slate-800 p-6 rounded-xl border border-slate-700">
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Company Name</label>
              <input required className="w-full p-2 bg-slate-700 rounded border border-slate-600" onChange={e => setForm({...form, company_name: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Job Title</label>
              <input required className="w-full p-2 bg-slate-700 rounded border border-slate-600" onChange={e => setForm({...form, job_title: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Location (City)</label>
              <input required className="w-full p-2 bg-slate-700 rounded border border-slate-600" onChange={e => setForm({...form, location: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">State (e.g. NY)</label>
              <input required className="w-full p-2 bg-slate-700 rounded border border-slate-600" onChange={e => setForm({...form, job_state: e.target.value})} />
            </div>
          </div>

          <hr className="border-slate-700" />

          <div className="grid md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block mb-1">Rating (0-5)</label>
              <input type="number" step="0.1" value={form.rating} className="w-full p-2 bg-slate-700 rounded" onChange={e => setForm({...form, rating: parseFloat(e.target.value)})} />
            </div>
            <div>
              <label className="block mb-1">Year Founded</label>
              <input type="number" value={form.founded} className="w-full p-2 bg-slate-700 rounded" onChange={e => setForm({...form, founded: parseInt(e.target.value)})} />
            </div>
            <div>
              <label className="block mb-1">Seniority</label>
              <select className="w-full p-2 bg-slate-700 rounded" onChange={e => setForm({...form, seniority: e.target.value})}>
                <option value="na">N/A</option>
                <option value="jr">Junior</option>
                <option value="sr">Senior</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Required Skills</label>
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-3 bg-slate-900 rounded border border-slate-700">
              {skillsList.map(s => (
                <button 
                  type="button" 
                  key={s} 
                  onClick={() => toggleSkill(s)}
                  className={`px-3 py-1 rounded-full text-xs transition ${form.skills.includes(s) ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-400 hover:bg-slate-600'}`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <button 
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-lg font-bold text-white transition disabled:opacity-50"
          >
            {loading ? "Calculating..." : "Predict Salary"}
          </button>
        </form>

        {/* RESULTS SECTION */}
<div className="space-y-6">
  <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 min-h-[300px] flex flex-col items-center justify-center text-center">
    {result ? (
      <>
        <p className="text-slate-400 uppercase text-xs tracking-widest mb-2">
          Estimated Annual Salary ({result.currency})
        </p>
        <h2 className="text-5xl font-black text-emerald-400 mb-4">
          {/* Use predicted_salary instead of estimated_salary */}
          ${result.predicted_salary?.toLocaleString()}
        </h2>
        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700 w-full">
          <p className="text-sm text-slate-300">Confidence Interval</p>
          <p className="text-lg font-mono text-indigo-300">
            {/* Use range_min and range_max */}
            ${result.range_min?.toLocaleString()} - ${result.range_max?.toLocaleString()}
          </p>
        </div>
        
        {/* Optional: Show which skills actually influenced the price */}
        <div className="mt-6 w-full text-left">
          <p className="text-xs text-slate-500 mb-2 uppercase font-bold">Skills Factored In:</p>
          <div className="flex flex-wrap gap-1">
            {result.skills_used?.map((s: string) => (
              <span key={s} className="bg-slate-700 text-slate-300 px-2 py-0.5 rounded text-[10px]">
                {s}
              </span>
            ))}
          </div>
        </div>
      </>
    ) : (
      <p className="text-slate-500 italic">Fill out the form to generate a prediction</p>
    )}
  </div>
</div>
      </div>
    </div>
  );
}