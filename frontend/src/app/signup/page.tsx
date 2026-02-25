"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SignUp() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch("/api/auth/signUp", { // Note the /api prefix
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    if (res.ok) router.push("/login");
    else alert("Signup failed");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-900 text-white">
      <form onSubmit={handleSubmit} className="p-8 bg-slate-800 rounded-xl shadow-lg w-96 border border-slate-700">
        <h2 className="text-2xl font-bold mb-6 text-center">Create Account</h2>
        <input 
          className="w-full p-2 mb-4 bg-slate-700 rounded border border-slate-600" 
          placeholder="Username" 
          onChange={e => setForm({...form, username: e.target.value})} 
        />
        <input 
          className="w-full p-2 mb-4 bg-slate-700 rounded border border-slate-600" 
          placeholder="Email" 
          onChange={e => setForm({...form, email: e.target.value})} 
        />
        <input 
          type="password" 
          className="w-full p-2 mb-6 bg-slate-700 rounded border border-slate-600" 
          placeholder="Password" 
          onChange={e => setForm({...form, password: e.target.value})} 
        />
        <button className="w-full bg-blue-600 hover:bg-blue-500 py-2 rounded font-semibold transition">Sign Up</button>
      </form>
    </div>
  );
}