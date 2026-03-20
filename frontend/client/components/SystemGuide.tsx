'use client';

import React from 'react';
import { motion } from 'framer-motion';

export default function Guide() {
  const steps = [
    { title: 'Voice Input', desc: 'Click the mic and use natural language.' },
    { title: 'AI Processing', desc: 'Gemini 2.0 parses your intent instantly.' },
    { title: 'Dash Navigation', desc: 'The UI switches tabs based on context.' },
    { title: 'Compliance', desc: 'Every action is logged in the Audit Trail.' }
  ];

  return (
    <div className="p-6 bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-700">
      <h2 className="text-2xl font-bold text-white mb-4">📘 System Walkthrough</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map((step, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="p-4 bg-slate-900/50 rounded-lg"
          >
            <h3 className="text-blue-400 font-bold">{step.title}</h3>
            <p className="text-slate-400 text-sm">{step.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
