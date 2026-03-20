"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, Plus, CheckCircle2, Clock, AlertCircle, LayoutDashboard, Settings, User, Search, Bell, Loader, Volume2, Trash2, ArrowRight, Zap, Calendar, Tag, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { getTasks, createTask, updateTask, processVoiceCommand, deleteTask, seedDemoData } from "@/lib/api";

export default function Home() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceFeedback, setVoiceFeedback] = useState("");
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showDueDatePicker, setShowDueDatePicker] = useState<number | null>(null);
  const recognitionRef = useRef<any>(null);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'm' || e.key === 'M') {
        e.preventDefault();
        startVoiceRecognition();
      }
      if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        const searchBox = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement;
        searchBox?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Filter tasks based on search and category
  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (task.description?.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = !selectedCategory || task.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(tasks.map(t => t.category).filter(Boolean)));
  const stats = {
    total: filteredTasks.length,
    todo: filteredTasks.filter(t => !t.status || t.status === "Todo").length,
    progress: filteredTasks.filter(t => t.status === "InProgress" || t.status === "In Progress").length,
    done: filteredTasks.filter(t => t.status === "Done").length,
  };

  const startVoiceRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceFeedback("❌ Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript("");
      setVoiceFeedback("🎤 Listening...");
    };

    recognition.onresult = (event: any) => {
      let interimTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptSegment = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setTranscript(transcriptSegment);
        } else {
          interimTranscript += transcriptSegment;
        }
      }
      if (interimTranscript) {
        setVoiceFeedback(`Interim: "${interimTranscript}"`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      setVoiceFeedback(`❌ Error: ${event.error}`);
      setIsListening(false);
    };

    recognition.start();
  };

  const handleProcessVoice = async () => {
    if (!transcript.trim()) return;

    setIsProcessing(true);
    setVoiceFeedback("⏳ Processing your command...");

    try {
      const result = await processVoiceCommand(transcript);
      
      if (result.status === "success") {
        setVoiceFeedback(`✅ ${result.message}`);
        if (result.task) {
          setTasks([...tasks, result.task]);
        } else {
          // Reload tasks to get any updates
          await loadTasks();
        }
      } else {
        setVoiceFeedback(`❌ ${result.message}`);
      }

      // Clear transcript after processing
      setTimeout(() => {
        setTranscript("");
      }, 2000);
    } catch (err) {
      setVoiceFeedback(`❌ Error: ${err}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAddNewTask = async () => {
    try {
      const newTask = await createTask({ 
        title: "New Task via Dashboard", 
        priority: "Medium" 
      });
      setTasks([...tasks, newTask]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateTaskStatus = async (taskId: number, newStatus: string) => {
    try {
      const updatedTask = await updateTask(taskId, { status: newStatus });
      setTasks(tasks.map(t => t.id === taskId ? updatedTask : t));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleSeedData = async () => {
    try {
      await seedDemoData();
      await loadTasks();
      setVoiceFeedback("✅ Demo data loaded successfully!");
    } catch (err) {
      console.error(err);
      setVoiceFeedback("❌ Failed to load demo data");
    }
  };

  return (
    <main className="min-h-screen p-8 bg-transparent text-white font-sans selection:bg-blue-500/30">
      {/* Sidebar */}
      <nav className="fixed left-0 top-0 h-full w-20 flex flex-col items-center py-10 space-y-10 nav-blur z-50">
        <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 ring-1 ring-white/20">
          <LayoutDashboard size={22} className="text-white" />
        </div>
        <div className="flex-1 flex flex-col space-y-8 pt-4">
          <NavItem icon={<Clock size={22} />} />
          <NavItem icon={<CheckCircle2 size={22} />} />
          <NavItem icon={<AlertCircle size={22} />} />
          <NavItem icon={<Search size={22} />} />
        </div>
        <div className="flex flex-col space-y-8 pb-4">
          <NavItem icon={<Bell size={22} />} />
          <NavItem icon={<Settings size={22} />} />
          <div className="w-10 h-10 rounded-full border border-white/10 overflow-hidden bg-white/5 flex items-center justify-center">
             <User size={20} className="text-gray-400" />
          </div>
        </div>
      </nav>

      {/* Hero Content */}
      <div className="ml-24 max-w-7xl mx-auto pt-4">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-16 gap-6">
          <div>
            <h1 className="text-5xl font-extrabold text-gradient tracking-tight">
              VoiceFlow
            </h1>
            <p className="text-gray-400 mt-3 text-lg font-medium opacity-80">
              Command your productivity with natural AI workflows.
            </p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={handleSeedData}
              className="bg-purple-600 text-white font-bold px-6 py-3.5 rounded-full flex items-center gap-2 hover:bg-purple-700 active:scale-95 transition-all shadow-xl shadow-purple-600/30"
            >
              <Zap size={20} />
              <span>Load Demo</span>
            </button>
            <button 
              onClick={handleAddNewTask}
              className="bg-white text-black font-bold px-8 py-3.5 rounded-full flex items-center gap-2 hover:bg-white/90 active:scale-95 transition-all shadow-xl shadow-white/10"
            >
              <Plus size={20} />
              <span>Create Task</span>
            </button>
          </div>
        </header>

        {/* Search & Filter Bar */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search tasks... (Press S to focus)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 focus:bg-white/10 transition-all"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  <X size={18} />
                </button>
              )}
            </div>
          </div>

          {/* Category Filter */}
          {categories.length > 0 && (
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                  !selectedCategory
                    ? "bg-blue-600 text-white"
                    : "bg-white/5 text-gray-400 hover:bg-white/10"
                }`}
              >
                All
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-all flex items-center gap-1 ${
                    selectedCategory === cat
                      ? "bg-purple-600 text-white"
                      : "bg-white/5 text-gray-400 hover:bg-white/10"
                  }`}
                >
                  <Tag size={14} />
                  {cat}
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* Voice Command Display */}
        {transcript && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 mb-8 border border-blue-500/20 rounded-2xl"
          >
            <div className="flex items-start gap-3">
              <Volume2 size={20} className="text-blue-400 mt-1 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-gray-400 mb-2">Voice Command:</p>
                <p className="text-xl text-white font-semibold">{transcript}</p>
              </div>
              {transcript && !isProcessing && (
                <button
                  onClick={handleProcessVoice}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold text-sm whitespace-nowrap transition-colors"
                >
                  Process
                </button>
              )}
            </div>
            {voiceFeedback && (
              <p className="text-sm text-yellow-400 mt-3">{voiceFeedback}</p>
            )}
          </motion.div>
        )}

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
          <StatCard title="Total Tasks" value={stats.total.toString()} color="blue" description="Active ongoing work" />
          <StatCard title="To Do" value={stats.todo.toString()} color="yellow" description="Not started yet" />
          <StatCard title="In Progress" value={stats.progress.toString()} color="purple" description="Current sprint focus" />
          <StatCard title="Completed" value={stats.done.toString()} color="green" description="Finished tasks" />
        </div>

        {/* Kanban Board */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          <BoardColumn 
            title="Open" 
            tasks={filteredTasks.filter(t => t.status === "Todo" || !t.status)} 
            color="blue" 
            onUpdateStatus={handleUpdateTaskStatus}
            onDelete={handleDeleteTask}
          />
          <BoardColumn 
            title="Running" 
            tasks={filteredTasks.filter(t => t.status === "InProgress" || t.status === "In Progress")} 
            color="purple" 
            onUpdateStatus={handleUpdateTaskStatus}
            onDelete={handleDeleteTask}
          />
          <BoardColumn 
            title="Finished" 
            tasks={filteredTasks.filter(t => t.status === "Done")} 
            color="green" 
            onUpdateStatus={handleUpdateTaskStatus}
            onDelete={handleDeleteTask}
          />
        </div>
      </div>

      {/* Floating Voice Control */}
      <div className="fixed bottom-12 right-12 z-50 flex items-center gap-4">
        <AnimatePresence>
          {(isListening || isProcessing) && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="glass-card px-6 py-3 text-blue-400 font-semibold flex items-center gap-3"
            >
              {isProcessing ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
                  </span>
                  Listening...
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={isListening ? () => setIsListening(false) : startVoiceRecognition}
          className={`w-16 h-16 rounded-full flex items-center justify-center font-bold text-white shadow-2xl transition-all ${
            isListening || isProcessing
              ? "bg-red-600 hover:bg-red-700 shadow-red-500/50"
              : "bg-blue-600 hover:bg-blue-700 shadow-blue-500/50"
          }`}
        >
          <Mic size={28} />
        </motion.button>
      </div>
    </main>
  );
}

function NavItem({ icon }: { icon: React.ReactNode }) {
  return (
    <button className="text-gray-500 hover:text-blue-400 transition-all p-3 hover:bg-blue-400/5 rounded-2xl cursor-pointer">
      {icon}
    </button>
  );
}

function StatCard({ title, value, color, description }: { title: string, value: string, color: string, description: string }) {
  const accentColors: any = {
    blue: "from-blue-500/20 to-transparent border-blue-500/20 text-blue-400",
    purple: "from-purple-500/20 to-transparent border-purple-500/20 text-purple-400",
    green: "from-green-500/20 to-transparent border-green-500/20 text-green-400",
  };
  return (
    <div className={`glass-card p-8 bg-gradient-to-br ${accentColors[color]} relative group`}>
      <h3 className="text-gray-500 text-sm font-bold uppercase tracking-widest">{title}</h3>
      <p className="text-5xl font-black mt-3 tracking-tighter">{value}</p>
      <p className="text-xs text-gray-400 mt-4 font-medium opacity-60 underline underline-offset-4 decoration-white/10">{description}</p>
    </div>
  );
}

function BoardColumn({ 
  title, 
  tasks, 
  color,
  onUpdateStatus,
  onDelete
}: { 
  title: string, 
  tasks: any[], 
  color: string,
  onUpdateStatus: (id: number, status: string) => void,
  onDelete: (id: number) => void
}) {
  const dotColors: any = {
    blue: "bg-blue-500",
    purple: "bg-purple-500",
    green: "bg-green-500",
  };

  const getNextStatus = (current: string) => {
    if (current === "Todo" || !current) return "InProgress";
    if (current === "InProgress" || current === "In Progress") return "Done";
    return "Todo";
  };

  const getNextStatusLabel = (current: string) => {
    if (current === "Todo" || !current) return "Start";
    if (current === "InProgress" || current === "In Progress") return "Complete";
    return "Reopen";
  };

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex items-center justify-between pb-2 border-b border-white/5">
        <h2 className="text-lg font-bold flex items-center gap-3 uppercase tracking-widest text-gray-400">
          <span className={`w-2 h-2 rounded-full ${dotColors[color]} shadow-[0_0_8px_rgba(var(--tw-color-blue-500),0.5)]`}></span>
          <span>{title}</span>
        </h2>
        <span className="text-sm bg-white/5 px-4 py-1 rounded-full font-mono text-gray-500 border border-white/5">
          {tasks.length}
        </span>
      </div>
      <div className="space-y-4 min-h-[400px]">
        {tasks.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-500 text-sm">
            <p>No tasks yet. Create one or use voice commands!</p>
          </div>
        ) : (
          tasks.map((task, idx) => (
            <motion.div 
              key={task.id || idx}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="glass-card p-5 flex flex-col gap-3 border-l-2 border-l-transparent hover:border-l-blue-500 border-white/5 group hover:shadow-lg hover:shadow-blue-500/10 transition-all"
            >
              {/* Header with priority badge */}
              <div className="flex justify-between items-start gap-3">
                <span className={`text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap ${
                  task.priority === 'High' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                  task.priority === 'Low' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                  'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                }`}>
                  {task.priority || 'Medium'}
                </span>
                <button
                  onClick={() => onDelete(task.id)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded text-red-400"
                  title="Delete task"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              {/* Task title */}
              <h3 className="font-semibold text-white leading-snug text-sm group-hover:text-blue-300 transition-colors">
                {task.title}
              </h3>

              {/* Task description */}
              {task.description && (
                <p className="text-xs text-gray-400 line-clamp-2">
                  {task.description}
                </p>
              )}

              {/* Status update button */}
              <button
                onClick={() => onUpdateStatus(task.id, getNextStatus(task.status))}
                className="mt-2 w-full py-2 bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/30 rounded-lg text-blue-300 text-xs font-semibold flex items-center justify-center gap-2 transition-colors group/btn"
              >
                <ArrowRight size={14} className="group-hover/btn:translate-x-1 transition-transform" />
                {getNextStatusLabel(task.status)}
              </button>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
