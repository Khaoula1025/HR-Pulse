"use client";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

function JobsContent() {
  const searchParams = useSearchParams();
  const [skillsList, setSkillsList] = useState<string[]>([]);
  const [selectedSkill, setSelectedSkill] = useState(searchParams.get("skill") || "");
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 1. Fetch skills for the dropdown (from predictor endpoint)
  useEffect(() => {
    fetch("/api/predict/skills", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setSkillsList(data.skills))
      .catch(() => setError("Failed to load skills list"));
  }, []);

  // 2. Fetch jobs function with credentials
  const handleSearch = async () => {
    setLoading(true);
    setError("");
    try {
      const url = selectedSkill
        ? `/api/jobs/?skill=${encodeURIComponent(selectedSkill)}`
        : "/api/jobs/";

      const res = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });

      if (res.status === 401) {
        setError("Session expired. Please login again.");
        return;
      }

      const data = await res.json();
      setJobs(data);
    } catch (err) {
      setError("Failed to fetch jobs.");
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    handleSearch();
  }, []);

  return (
    <div className="p-8 bg-slate-900 min-h-screen text-slate-100">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-indigo-400">Browse Jobs</h1>

        {/* SEARCH SECTION: Select List + Button */}
        <div className="flex flex-col md:flex-row gap-4 mb-10 p-6 bg-slate-800 rounded-xl border border-slate-700 shadow-xl">
          <div className="flex-1">
            <label className="block text-sm text-slate-400 mb-2 font-medium">Filter by Required Skill</label>
            <select
              className="w-full bg-slate-700 border border-slate-600 p-3 rounded-lg text-white focus:ring-2 focus:ring-indigo-500 outline-none"
              value={selectedSkill}
              onChange={(e) => setSelectedSkill(e.target.value)}
            >
              <option value="">All Skills / No Filter</option>
              {skillsList.map((skill) => (
                <option key={skill} value={skill}>{skill}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="w-full md:w-auto bg-indigo-600 hover:bg-indigo-500 px-8 py-3 rounded-lg font-bold transition disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search Jobs"}
            </button>
          </div>
        </div>

        {error && <p className="text-red-400 mb-6 bg-red-400/10 p-3 rounded border border-red-400/20">{error}</p>}

        {/* JOBS LIST */}
        <div className="grid md:grid-cols-2 gap-6">
          {jobs.length > 0 ? (
            jobs.map((job: any) => (
              <div key={job.id} className="bg-slate-800 p-6 rounded-xl border border-slate-700 hover:border-indigo-500/50 transition">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-white">{job.job_title}</h3>
                    <p className="text-indigo-300 text-sm">{job.company_name}</p>
                  </div>
                  <span className="text-emerald-400 font-mono text-sm bg-emerald-400/10 px-2 py-1 rounded">
                    {job.location}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mt-4">
                  {job.skills_extracted?.map((s: string) => (
                    <span key={s} className="bg-slate-900 text-slate-400 border border-slate-700 px-2 py-1 rounded text-xs">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))
          ) : (
            !loading && (
              <p className="text-slate-500 col-span-2 text-center py-20 border-2 border-dashed border-slate-800 rounded-xl">
                No jobs found matching this skill.
              </p>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-slate-400">Loading...</div>}>
      <JobsContent />
    </Suspense>
  );
}