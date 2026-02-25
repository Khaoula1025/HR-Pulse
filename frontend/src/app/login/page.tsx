"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const [form, setForm] = useState({ identifier: "", password: "" });
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    if (res.ok) router.push("/predict");
    else alert("Invalid credentials");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-900 text-white">
      <form onSubmit={handleLogin} className="p-8 bg-slate-800 rounded-xl shadow-lg w-96 border border-slate-700">
        <h2 className="text-2xl font-bold mb-6 text-center">Welcome Back</h2>
        <input 
          className="w-full p-2 mb-4 bg-slate-700 rounded border border-slate-600" 
          placeholder="Email or Username" 
          onChange={e => setForm({...form, identifier: e.target.value})} 
        />
        <input 
          type="password" 
          className="w-full p-2 mb-6 bg-slate-700 rounded border border-slate-600" 
          placeholder="Password" 
          onChange={e => setForm({...form, password: e.target.value})} 
        />
        <button className="w-full bg-green-600 hover:bg-green-500 py-2 rounded font-semibold transition">Login</button>
      </form>
    </div>
  );
}