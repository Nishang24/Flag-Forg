"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useRouter } from "next/navigation";
import { ArrowLeft, User, Activity, CheckCircle2, Clock, LogOut } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

interface Task {
  id: number;
  title: string;
  status: string;
  priority: string;
  created_at?: string;
}

export default function Profile() {
  const { user, token, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const fetchUserTasks = async () => {
      try {
        const res = await fetch("http://localhost:8000/tasks/", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setTasks(data);
        }
      } catch (err) {
        console.error("Failed to load tasks", err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserTasks();
  }, [isAuthenticated, token, router]);

  const completedTasks = tasks.filter(t => t.status === "Done");
  const pendingTasks = tasks.filter(t => t.status !== "Done");

  if (!isAuthenticated || !user) return null;

  return (
    <main className="min-h-screen p-8 bg-transparent text-white font-sans selection:bg-purple-500/30">
      <div className="max-w-4xl mx-auto">
        {/* Header Navigation */}
        <header className="flex items-center justify-between mb-12">
          <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
            <ArrowLeft size={20} />
            <span className="font-medium">Back to Dashboard</span>
          </Link>
          <button 
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl transition-all border border-red-500/20"
          >
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </header>

        {/* Profile Card */}
        <div className="glass-card p-10 rounded-3xl mb-12 flex flex-col md:flex-row gap-8 items-center border border-white/10 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
          <div className="w-32 h-32 rounded-full border-4 border-white/10 overflow-hidden bg-white/5 flex items-center justify-center flex-shrink-0">
            <User size={64} className="text-gray-400" />
          </div>
          <div className="flex-1 text-center md:text-left">
            <h1 className="text-4xl font-bold mb-2">{user.email}</h1>
            <p className="text-gray-400 flex items-center justify-center md:justify-start gap-2">
              <span className="px-3 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-full text-xs font-bold uppercase tracking-wider">
                {user.role}
              </span>
              <span>•</span>
              <span>VoiceFlow Licensed Agent</span>
            </p>
          </div>
          
          <div className="flex gap-6 mt-6 md:mt-0">
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{tasks.length}</p>
              <p className="text-sm text-gray-500">Total Tasks</p>
            </div>
          </div>
        </div>

        {/* Task Archive */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2 text-green-400">
              <CheckCircle2 size={24} /> Completed Archive
            </h2>
            <div className="space-y-4">
              {loading ? (
                <p className="text-gray-500">Loading...</p>
              ) : completedTasks.length === 0 ? (
                <div className="glass-card p-6 text-center text-gray-400">No completed tasks yet.</div>
              ) : (
                completedTasks.map(task => (
                  <motion.div key={task.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 border border-white/5 opacity-70">
                    <h3 className="font-semibold line-through text-gray-300">{task.title}</h3>
                    <div className="flex gap-2 mt-3">
                      <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded-md">Done</span>
                      <span className="px-2 py-1 bg-white/5 text-gray-400 text-xs rounded-md">{task.priority} Priority</span>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </div>

          <div className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2 text-purple-400">
              <Clock size={24} /> Active Operations
            </h2>
            <div className="space-y-4">
              {loading ? (
                <p className="text-gray-500">Loading...</p>
              ) : pendingTasks.length === 0 ? (
                <div className="glass-card p-6 text-center text-gray-400">No active tasks.</div>
              ) : (
                pendingTasks.map(task => (
                  <motion.div key={task.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.1)]">
                    <h3 className="font-semibold">{task.title}</h3>
                    <div className="flex gap-2 mt-3">
                      <span className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs rounded-md">{task.status}</span>
                      <span className="px-2 py-1 bg-white/5 text-gray-400 text-xs rounded-md">{task.priority} Priority</span>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
