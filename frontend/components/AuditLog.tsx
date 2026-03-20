"use client";

import { useState, useEffect } from "react";
import { ChevronDown, Clock, Eye, EyeOff } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { getTaskHistory, getAuditStats } from "@/lib/api";

export function AuditLogPanel({ taskId }: { taskId: number }) {
  const [isOpen, setIsOpen] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && taskId) {
      loadHistory();
    }
  }, [isOpen, taskId]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getTaskHistory(taskId, 50);
      setHistory(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "created":
        return "text-green-400 bg-green-500/10";
      case "updated":
        return "text-blue-400 bg-blue-500/10";
      case "deleted":
        return "text-red-400 bg-red-500/10";
      case "voice_command":
        return "text-purple-400 bg-purple-500/10";
      default:
        return "text-gray-400 bg-gray-500/10";
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case "voice":
        return "🎤";
      case "api":
        return "⚙️";
      case "workflow":
        return "⚡";
      case "ui":
        return "🖱️";
      default:
        return "📝";
    }
  };

  return (
    <div className="mt-6 border-t border-white/10 pt-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm font-semibold text-gray-400 hover:text-white transition-colors w-full py-3"
      >
        <Clock size={16} />
        <span>Audit History</span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown size={16} />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="mt-4 space-y-3 max-h-96 overflow-y-auto">
              {loading ? (
                <div className="text-center py-8 text-gray-500">
                  Loading history...
                </div>
              ) : history.length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">
                  No changes yet
                </div>
              ) : (
                history.map((log, idx) => (
                  <motion.div
                    key={log.id || idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="glass-card p-3 text-xs space-y-1 border border-white/5 rounded-lg hover:border-white/20 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded font-semibold ${getActionColor(log.action)}`}>
                          {log.action}
                        </span>
                        <span className="text-gray-500">
                          {getSourceColor(log.source)} {log.source}
                        </span>
                      </div>
                      <span className="text-gray-600">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    {log.field_name && (
                      <div className="text-gray-400 space-y-0.5">
                        <p>
                          <span className="font-semibold text-white">{log.field_name}</span>
                        </p>
                        {log.old_value && log.new_value && (
                          <p>
                            <span className="text-red-400">{log.old_value}</span>
                            {" → "}
                            <span className="text-green-400">{log.new_value}</span>
                          </p>
                        )}
                      </div>
                    )}

                    {log.details && (
                      <p className="text-gray-500 italic">{log.details}</p>
                    )}
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function AuditStatsDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await getAuditStats();
      setStats(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) return null;

  return (
    <div className="glass-card p-6 rounded-2xl border border-white/10 mt-8">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <Clock size={20} className="text-blue-400" />
        Audit Dashboard
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatItem
          label="Total Events"
          value={stats.total_events || 0}
          color="blue"
        />
        {Object.entries(stats.by_action || {}).map(([action, count]: [string, any]) => (
          <StatItem
            key={action}
            label={action.charAt(0).toUpperCase() + action.slice(1)}
            value={count}
            color="purple"
          />
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-400">
        <p>
          Most changed field: <span className="text-white font-semibold">{stats.most_changed_field}</span>
        </p>
      </div>
    </div>
  );
}

function StatItem({ label, value, color }: { label: string; value: number; color: string }) {
  const colors = {
    blue: "from-blue-500/20 to-transparent border-blue-500/20",
    purple: "from-purple-500/20 to-transparent border-purple-500/20",
    green: "from-green-500/20 to-transparent border-green-500/20",
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color as keyof typeof colors]} border rounded-lg p-3`}>
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
