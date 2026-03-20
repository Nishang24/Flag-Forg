"use client";

import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { Mic, Lock, Mail, Loader } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // 1. Get Token
      const response = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password: password }),
      });

      if (!response.ok) {
        throw new Error("Invalid email or password");
      }

      const data = await response.json();
      const token = data.access_token;
      
      // 2. Get User Payload
      const userRes = await fetch("http://localhost:8000/api/users/me", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (!userRes.ok) throw new Error("Failed to fetch user context");
      const userData = await userRes.json();

      login(token, userData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-8 bg-transparent text-white font-sans selection:bg-blue-500/30">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md glass-card p-10 flex flex-col items-center"
      >
        <div className="w-16 h-16 bg-blue-600/20 shadow-[0_0_30px_rgba(59,130,246,0.5)] rounded-2xl flex items-center justify-center mb-6">
          <Mic size={32} className="text-blue-400" />
        </div>
        <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
        <p className="text-gray-400 mb-8 text-center max-w-xs">Log in to command your enterprise tasks via VoiceFlow.</p>
        
        {error && (
          <div className="w-full bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-xl mb-6 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="w-full space-y-5">
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              className="w-full bg-black/20 border border-white/10 rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:bg-white/5 transition-all"
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full bg-black/20 border border-white/10 rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:bg-white/5 transition-all"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center mt-4"
          >
            {loading ? <Loader className="animate-spin" size={24} /> : "Sign In"}
          </button>
        </form>
        
        <p className="text-gray-400 mt-8 text-sm">
          Don't have an account? <Link href="/register" className="text-blue-400 hover:text-blue-300 font-medium">Create one</Link>
        </p>
      </motion.div>
    </main>
  );
}
