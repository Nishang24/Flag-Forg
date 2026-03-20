"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { Mic, Lock, Mail, Loader, Key } from "lucide-react";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to register");
      }

      router.push("/login");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-8 bg-transparent text-white font-sans selection:bg-purple-500/30">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md glass-card p-10 flex flex-col items-center border border-purple-500/20"
      >
        <div className="w-16 h-16 bg-purple-600/20 shadow-[0_0_30px_rgba(168,85,247,0.4)] rounded-2xl flex items-center justify-center mb-6">
          <Key size={32} className="text-purple-400" />
        </div>
        <h1 className="text-3xl font-bold mb-2">Create Account</h1>
        <p className="text-gray-400 mb-8 text-center max-w-xs">Join VoiceFlow today and control your lifecycle with AI.</p>
        
        {error && (
          <div className="w-full bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-xl mb-6 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="w-full space-y-5">
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Corporate Email"
              className="w-full bg-black/20 border border-white/10 rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:bg-white/5 transition-all"
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Master Password"
              className="w-full bg-black/20 border border-white/10 rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:bg-white/5 transition-all"
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input 
              type="password" 
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm Password"
              className="w-full bg-black/20 border border-white/10 rounded-xl pl-12 pr-4 py-4 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:bg-white/5 transition-all"
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center mt-4 border border-purple-500/50 focus:ring-2 ring-purple-500"
          >
            {loading ? <Loader className="animate-spin" size={24} /> : "Initialize Account"}
          </button>
        </form>
        
        <p className="text-gray-400 mt-8 text-sm">
          Already have an account? <Link href="/login" className="text-purple-400 hover:text-purple-300 font-medium">Sign In</Link>
        </p>
      </motion.div>
    </main>
  );
}
