'use client';

import React, { useState, useEffect } from 'react';
import { getTasks, getWorkers, getInventory, getAuditLogs, processVoiceCommand } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Loader } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('tasks');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [qualityReports, setQualityReports] = useState([]);
  const [equipment, setEquipment] = useState([]);
  const [safetyIncidents, setSafetyIncidents] = useState([]);
  const [orders, setOrders] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [responseMessage, setResponseMessage] = useState('');
  const [newItemForm, setNewItemForm] = useState({ name: '', category: '', quantity: 0 });
  const [loading, setLoading] = useState(false);

  // Initialize speech recognition
  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition not supported in this browser');
      return null;
    }
    return new SpeechRecognition();
  };

  // Fetch all data on mount and every 5 seconds
  useEffect(() => {
    const fetchAllData = async () => {
      try {
        const [tasksData, workersData, inventoryData, auditData] = await Promise.all([
          getTasks(),
          getWorkers(),
          getInventory(),
          getAuditLogs()
        ]);
        
        setTasks(tasksData || []);
        setWorkers(workersData || []);
        setInventory(inventoryData || []);
        setAuditLogs(auditData || []);

        // Fetch system status
        const statusResponse = await fetch('http://127.0.0.1:8000/system-status').catch(() => null);
        if (statusResponse?.ok) {
          const status = await statusResponse.json();
          setSystemStatus(status);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Voice command handler
  const startListening = async () => {
    const recognition = initSpeechRecognition();
    if (!recognition) return;

    setIsListening(true);
    recognition.start();

    recognition.onresult = async (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join('');

      setIsListening(false);

      if (transcript.toLowerCase().includes('cancel')) {
        setResponseMessage('Command cancelled');
        return;
      }

      setLoading(true);
      try {
        const result = await processVoiceCommand(transcript);
        setResponseMessage(result.audio_response || result.message);
        
        // Refresh data after voice command
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } catch (error) {
        setResponseMessage('Error processing command: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      setResponseMessage('Error: ' + event.error);
    };
  };

  const tabs = [
    { id: 'tasks', label: '📋 Tasks', icon: '✅' },
    { id: 'workers', label: '👥 Workers', icon: '👨' },
    { id: 'inventory', label: '📦 Inventory', icon: '📦' },
    { id: 'shifts', label: '⏰ Shifts', icon: '⏰' },
    { id: 'attendance', label: '📊 Attendance', icon: '📊' },
    { id: 'quality', label: '🔍 Quality', icon: '🔍' },
    { id: 'equipment', label: '⚙️ Equipment', icon: '⚙️' },
    { id: 'safety', label: '🚨 Safety', icon: '🚨' },
    { id: 'orders', label: '🛒 Orders', icon: '🛒' },
    { id: 'audit', label: '📝 Audit Logs', icon: '📝' }
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-xl border-b border-slate-700"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white">🎤 VoiceFlow</h1>
              <p className="text-slate-400">Kitchenware Industry Management</p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={startListening}
              disabled={isListening || loading}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold transition-all ${
                isListening
                  ? 'bg-red-500 text-white'
                  : loading
                  ? 'bg-slate-500 text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {isListening ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Listening...
                </>
              ) : loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Mic className="w-5 h-5" />
                  🎤 Voice Command
                </>
              )}
            </motion.button>
          </div>

          {responseMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-green-500/20 border border-green-500 text-green-200 rounded-lg text-sm"
            >
              {responseMessage}
            </motion.div>
          )}

          {systemStatus && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4"
            >
              <div className="bg-slate-800 rounded-lg p-3 border border-slate-700">
                <div className="text-slate-400 text-xs">Workers</div>
                <div className="text-xl font-bold text-white">{systemStatus.statistics?.total_workers || 0}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-3 border border-slate-700">
                <div className="text-slate-400 text-xs">Tasks</div>
                <div className="text-xl font-bold text-white">{systemStatus.statistics?.total_tasks || 0}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-3 border border-slate-700">
                <div className="text-slate-400 text-xs">Inventory</div>
                <div className="text-xl font-bold text-white">{systemStatus.statistics?.total_inventory_items || 0}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-3 border border-slate-700">
                <div className="text-slate-400 text-xs">Orders</div>
                <div className="text-xl font-bold text-white">{systemStatus.statistics?.open_orders || 0}</div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="bg-slate-800/50 px-4 py-3 overflow-x-auto">
          <div className="flex gap-2">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all font-medium ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {tab.label}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          {/* TASKS TAB */}
          {activeTab === 'tasks' && (
            <motion.div
              key="tasks"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {tasks.map((task) => (
                <motion.div
                  key={task.id}
                  whileHover={{ y: -5 }}
                  className="bg-slate-800 border border-slate-700 rounded-lg p-4 backdrop-blur-xl"
                >
                  <h3 className="text-lg font-bold text-white mb-2">{task.title}</h3>
                  <div className="space-y-2 text-sm text-slate-300">
                    <div>Priority: <span className="text-blue-400">{task.priority}</span></div>
                    <div>Status: <span className="text-green-400">{task.status}</span></div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* WORKERS TAB */}
          {activeTab === 'workers' && (
            <motion.div
              key="workers"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {workers.map((worker) => (
                <motion.div
                  key={worker.id}
                  whileHover={{ y: -5 }}
                  className="bg-slate-800 border border-slate-700 rounded-lg p-4 backdrop-blur-xl"
                >
                  <h3 className="text-lg font-bold text-white mb-2">{worker.name}</h3>
                  <div className="space-y-2 text-sm text-slate-300">
                    <div>Position: <span className="text-blue-400">{worker.position}</span></div>
                    <div>Department: <span className="text-purple-400">{worker.department}</span></div>
                    <div>Status: <span className="text-green-400">{worker.status}</span></div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* INVENTORY TAB */}
          {activeTab === 'inventory' && (
            <motion.div
              key="inventory"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {inventory.map((item) => (
                <motion.div
                  key={item.id}
                  whileHover={{ y: -5 }}
                  className="bg-slate-800 border border-slate-700 rounded-lg p-4 backdrop-blur-xl"
                >
                  <h3 className="text-lg font-bold text-white mb-2">{item.name}</h3>
                  <div className="space-y-2 text-sm text-slate-300">
                    <div>Category: <span className="text-blue-400">{item.category}</span></div>
                    <div>Quantity: <span className="text-green-400">{item.quantity} {item.unit}</span></div>
                    <div>SKU: <span className="text-slate-400">{item.sku}</span></div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* SHIFTS TAB */}
          {activeTab === 'shifts' && (
            <motion.div
              key="shifts"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 backdrop-blur-xl">
                <h2 className="text-2xl font-bold text-white mb-4">⏰ Shift Management</h2>
                <p className="text-slate-400">Create and manage work shifts, assign workers to shifts, and track attendance</p>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">Create Shift</button>
                  <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">Assign Worker</button>
                </div>
              </div>
            </motion.div>
          )}

          {/* ATTENDANCE TAB */}
          {activeTab === 'attendance' && (
            <motion.div
              key="attendance"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 backdrop-blur-xl">
                <h2 className="text-2xl font-bold text-white mb-4">📊 Attendance Tracking</h2>
                <p className="text-slate-400">Track worker check-in/check-out times, overtime, and generate reports</p>
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">Check In</button>
                  <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg">Check Out</button>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">Daily Report</button>
                </div>
              </div>
            </motion.div>
          )}

          {/* QUALITY TAB */}
          {activeTab === 'quality' && (
            <motion.div
              key="quality"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 backdrop-blur-xl">
                <h2 className="text-2xl font-bold text-white mb-4">🔍 Quality Control</h2>
                <p className="text-slate-400">Record quality checks, inspect items, and generate quality reports</p>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">Record Check</button>
                  <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg">View Reports</button>
                </div>
              </div>
            </motion.div>
          )}

          {/* EQUIPMENT TAB */}
          {activeTab === 'equipment' && (
            <motion.div
              key="equipment"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 backdrop-blur-xl">
                <h2 className="text-2xl font-bold text-white mb-4">⚙️ Equipment Management</h2>
                <p className="text-slate-400">Register equipment, schedule maintenance, and track equipment alerts</p>
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">Register</button>
                  <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg">Maintenance</button>
                  <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg">Alerts</button>
                </div>
              </div>
            </motion.div>
          )}

          {/* SAFETY TAB */}
          {activeTab === 'safety' && (
            <motion.div
              key="safety"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 backdrop-blur-xl">
                <h2 className="text-2xl font-bold text-white mb-4">🚨 Safety Management</h2>
                <p className="text-slate-400">Report safety incidents, track compliance, and manage safety checks</p>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg">Report Incident</button>
                  <button className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg">Safety Check</button>
                </div>
              </div>
            </motion.div>
          )}

          {/* ORDERS TAB */}
          {activeTab === 'orders' && (
            <motion.div
              key="orders"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 backdrop-blur-xl">
                <h2 className="text-2xl font-bold text-white mb-4">🛒 Order Management</h2>
                <p className="text-slate-400">Create orders, track delivery, manage complaints and returns</p>
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">New Order</button>
                  <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg">Complaint</button>
                  <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg">Return</button>
                </div>
              </div>
            </motion.div>
          )}

          {/* AUDIT TAB */}
          {activeTab === 'audit' && (
            <motion.div
              key="audit"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="space-y-2">
                {auditLogs.slice(0, 10).map((log) => (
                  <motion.div
                    key={log.id}
                    whileHover={{ x: 5 }}
                    className="bg-slate-800 border border-slate-700 rounded-lg p-4 backdrop-blur-xl"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-semibold">{log.description}</p>
                        <p className="text-slate-500 text-sm">{log.action} - {log.entity_type}</p>
                      </div>
                      <p className="text-slate-400 text-xs">{new Date(log.timestamp).toLocaleString()}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
