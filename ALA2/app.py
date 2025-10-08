import React, { useState, useEffect, useRef } from 'react';
import { Shield, Play, Pause, RotateCcw, Download, Menu, X, Sun, Moon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MalwareSim = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [selectedMalware, setSelectedMalware] = useState('virus');
  const [infectionProb, setInfectionProb] = useState(0.3);
  const [networkSize, setNetworkSize] = useState(20);
  const [isRunning, setIsRunning] = useState(false);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [infectionData, setInfectionData] = useState([]);
  const [step, setStep] = useState(0);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  const colors = {
    virus: '#EF4444',
    worm: '#F59E0B',
    trojan: '#3B82F6'
  };

  // Initialize network
  useEffect(() => {
    initializeNetwork();
  }, [networkSize]);

  const initializeNetwork = () => {
    const newNodes = [];
    const newEdges = [];
    
    for (let i = 0; i < networkSize; i++) {
      newNodes.push({
        id: i,
        x: Math.random() * 600 + 50,
        y: Math.random() * 400 + 50,
        infected: i === 0,
        type: i === 0 ? selectedMalware : null,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5
      });
    }

    for (let i = 0; i < networkSize; i++) {
      const connections = Math.floor(Math.random() * 3) + 1;
      for (let j = 0; j < connections; j++) {
        const target = Math.floor(Math.random() * networkSize);
        if (target !== i && !newEdges.some(e => 
          (e.source === i && e.target === target) || 
          (e.source === target && e.target === i)
        )) {
          newEdges.push({ source: i, target });
        }
      }
    }

    setNodes(newNodes);
    setEdges(newEdges);
    setInfectionData([{ step: 0, infected: 1 }]);
    setStep(0);
  };

  // Simulation logic
  useEffect(() => {
    if (isRunning) {
      animationRef.current = setInterval(() => {
        setNodes(prevNodes => {
          const newNodes = [...prevNodes];
          let newInfections = 0;

          prevNodes.forEach((node, idx) => {
            if (node.infected) {
              edges.forEach(edge => {
                let targetId = null;
                if (edge.source === node.id) targetId = edge.target;
                if (edge.target === node.id) targetId = edge.source;

                if (targetId !== null && !newNodes[targetId].infected) {
                  let shouldInfect = false;
                  
                  if (selectedMalware === 'worm') {
                    shouldInfect = Math.random() < infectionProb * 1.5;
                  } else if (selectedMalware === 'virus') {
                    shouldInfect = Math.random() < infectionProb * 0.8;
                  } else if (selectedMalware === 'trojan') {
                    shouldInfect = Math.random() < infectionProb * 0.5;
                  }

                  if (shouldInfect) {
                    newNodes[targetId].infected = true;
                    newNodes[targetId].type = selectedMalware;
                    newInfections++;
                  }
                }
              });
            }

            // Node movement
            newNodes[idx].x += newNodes[idx].vx;
            newNodes[idx].y += newNodes[idx].vy;

            if (newNodes[idx].x < 30 || newNodes[idx].x > 670) newNodes[idx].vx *= -1;
            if (newNodes[idx].y < 30 || newNodes[idx].y > 470) newNodes[idx].vy *= -1;
          });

          return newNodes;
        });

        setStep(prev => {
          const newStep = prev + 1;
          const infected = nodes.filter(n => n.infected).length;
          setInfectionData(prevData => [...prevData, { step: newStep, infected }]);
          return newStep;
        });

        if (nodes.every(n => n.infected)) {
          setIsRunning(false);
        }
      }, 500);
    }

    return () => clearInterval(animationRef.current);
  }, [isRunning, nodes, edges, selectedMalware, infectionProb]);

  // Canvas drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges
    edges.forEach(edge => {
      const source = nodes[edge.source];
      const target = nodes[edge.target];
      if (source && target) {
        ctx.strokeStyle = darkMode ? '#4B5563' : '#E5E7EB';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
      }
    });

    // Draw nodes
    nodes.forEach(node => {
      ctx.beginPath();
      ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI);
      
      if (node.infected) {
        ctx.fillStyle = colors[node.type];
        ctx.shadowColor = colors[node.type];
        ctx.shadowBlur = 15;
      } else {
        ctx.fillStyle = darkMode ? '#6B7280' : '#D1D5DB';
        ctx.shadowBlur = 0;
      }
      
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }, [nodes, edges, darkMode]);

  const handleStart = () => {
    if (nodes.length === 0) initializeNetwork();
    setIsRunning(true);
  };

  const handlePause = () => setIsRunning(false);

  const handleReset = () => {
    setIsRunning(false);
    initializeNetwork();
  };

  const handleDownload = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Step,Infected Nodes\n"
      + infectionData.map(d => `${d.step},${d.infected}`).join("\n");
    const link = document.createElement("a");
    link.href = encodeURI(csvContent);
    link.download = "simulation_results.csv";
    link.click();
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-gray-100' : 'bg-[#F8FAFC] text-[#1E293B]'} transition-colors duration-300`}>
      {/* Navbar */}
      <nav className={`sticky top-0 z-50 ${darkMode ? 'bg-gray-800 shadow-xl' : 'bg-white shadow-md'} transition-all duration-300`}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-2xl font-bold">
            <Shield className="text-[#2563EB]" size={32} />
            <span className="bg-gradient-to-r from-[#2563EB] to-[#3B82F6] bg-clip-text text-transparent">MalSim</span>
          </div>
          
          <div className="hidden md:flex items-center gap-6">
            <a href="#" className="hover:text-[#2563EB] transition-colors">Home</a>
            <a href="#simulation" className="hover:text-[#2563EB] transition-colors">Simulation</a>
            <a href="#learn" className="hover:text-[#2563EB] transition-colors">Learn</a>
            <a href="#reports" className="hover:text-[#2563EB] transition-colors">Reports</a>
            <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>

          <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h1 className="text-5xl font-bold leading-tight">
              Explore Malware Behavior <span className="text-[#2563EB]">Safely</span>
            </h1>
            <p className="text-xl opacity-80">
              Simulate Viruses, Worms, and Trojans in a controlled environment. Learn how malware spreads through networks.
            </p>
            <button 
              onClick={() => document.getElementById('simulation').scrollIntoView({ behavior: 'smooth' })}
              className="px-8 py-4 bg-gradient-to-r from-[#2563EB] to-[#3B82F6] text-white rounded-lg font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300"
            >
              Start Simulation
            </button>
          </div>
          <div className="relative h-96">
            <div className="absolute inset-0 bg-gradient-to-br from-[#2563EB]/20 to-[#3B82F6]/20 rounded-3xl blur-3xl animate-pulse"></div>
            <canvas ref={canvasRef} width="700" height="500" className="relative z-10 w-full h-full rounded-3xl" />
          </div>
        </div>
      </section>

      {/* Simulation Section */}
      <section id="simulation" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold mb-12 text-center">Interactive Simulation</h2>
        
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Controls */}
          <div className={`lg:col-span-1 ${darkMode ? 'bg-gray-800' : 'bg-white'} p-6 rounded-2xl shadow-xl space-y-6`}>
            <div>
              <label className="block mb-2 font-semibold">Malware Type</label>
              <select 
                value={selectedMalware}
                onChange={(e) => setSelectedMalware(e.target.value)}
                className={`w-full p-3 rounded-lg border-2 ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'}`}
                disabled={isRunning}
              >
                <option value="virus">🦠 Virus</option>
                <option value="worm">🐛 Worm</option>
                <option value="trojan">🐴 Trojan</option>
              </select>
            </div>

            <div>
              <label className="block mb-2 font-semibold">Infection Probability: {infectionProb.toFixed(2)}</label>
              <input 
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                value={infectionProb}
                onChange={(e) => setInfectionProb(parseFloat(e.target.value))}
                className="w-full"
                disabled={isRunning}
              />
            </div>

            <div>
              <label className="block mb-2 font-semibold">Network Size: {networkSize}</label>
              <input 
                type="range"
                min="10"
                max="50"
                step="5"
                value={networkSize}
                onChange={(e) => setNetworkSize(parseInt(e.target.value))}
                className="w-full"
                disabled={isRunning}
              />
            </div>

            <div className="flex gap-2">
              {!isRunning ? (
                <button onClick={handleStart} className="flex-1 p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2">
                  <Play size={20} /> Start
                </button>
              ) : (
                <button onClick={handlePause} className="flex-1 p-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors flex items-center justify-center gap-2">
                  <Pause size={20} /> Pause
                </button>
              )}
              <button onClick={handleReset} className="flex-1 p-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center justify-center gap-2">
                <RotateCcw size={20} /> Reset
              </button>
            </div>

            <div className="pt-4 border-t border-gray-300 dark:border-gray-600">
              <p className="text-sm opacity-70">Step: {step}</p>
              <p className="text-sm opacity-70">Infected: {nodes.filter(n => n.infected).length} / {nodes.length}</p>
            </div>
          </div>

          {/* Network Visualization */}
          <div className={`lg:col-span-3 ${darkMode ? 'bg-gray-800' : 'bg-white'} p-6 rounded-2xl shadow-xl`}>
            <canvas ref={canvasRef} width="700" height="500" className="w-full h-full rounded-xl" />
          </div>
        </div>
      </section>

      {/* Education Section */}
      <section id="learn" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold mb-12 text-center">Learn About Malware</h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { type: 'virus', icon: '🦠', color: '#EF4444', title: 'Virus', desc: 'Infects files locally and spreads when files are shared or executed.' },
            { type: 'worm', icon: '🐛', color: '#F59E0B', title: 'Worm', desc: 'Self-replicates across networks rapidly without user interaction.' },
            { type: 'trojan', icon: '🐴', color: '#3B82F6', title: 'Trojan', desc: 'Disguised as legitimate software, activates malicious payload later.' }
          ].map((malware, idx) => (
            <div 
              key={idx}
              className={`${darkMode ? 'bg-gray-800' : 'bg-white'} p-8 rounded-2xl shadow-xl hover:scale-105 hover:shadow-2xl transition-all duration-300 cursor-pointer`}
            >
              <div className="text-6xl mb-4">{malware.icon}</div>
              <h3 className="text-2xl font-bold mb-3" style={{ color: malware.color }}>{malware.title}</h3>
              <p className="opacity-80">{malware.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Reports Section */}
      <section id="reports" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold mb-12 text-center">Simulation Results</h2>
        
        <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} p-8 rounded-2xl shadow-xl`}>
          <div className="mb-6 flex justify-between items-center">
            <h3 className="text-2xl font-semibold">Infection Spread Over Time</h3>
            <button 
              onClick={handleDownload}
              className="px-4 py-2 bg-[#2563EB] text-white rounded-lg hover:bg-[#1D4ED8] transition-colors flex items-center gap-2"
            >
              <Download size={20} /> Download CSV
            </button>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={infectionData}>
              <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#374151' : '#E5E7EB'} />
              <XAxis dataKey="step" stroke={darkMode ? '#9CA3AF' : '#6B7280'} />
              <YAxis stroke={darkMode ? '#9CA3AF' : '#6B7280'} />
              <Tooltip contentStyle={{ backgroundColor: darkMode ? '#1F2937' : '#FFFFFF', border: 'none', borderRadius: '8px' }} />
              <Legend />
              <Line type="monotone" dataKey="infected" stroke={colors[selectedMalware]} strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Footer */}
      <footer className={`${darkMode ? 'bg-gray-800' : 'bg-white'} mt-20 py-12 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4 text-center space-y-4">
          <div className="flex justify-center gap-8 mb-4">
            <a href="#" className="hover:text-[#2563EB] transition-colors">About</a>
            <a href="#" className="hover:text-[#2563EB] transition-colors">Privacy</a>
            <a href="#" className="hover:text-[#2563EB] transition-colors">Contact</a>
            <a href="#" className="hover:text-[#2563EB] transition-colors">GitHub</a>
          </div>
          <p className="text-sm opacity-70">
            ⚠️ Educational purposes only — no real malware is executed.
          </p>
          <p className="text-sm opacity-50">© 2025 MalSim. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default MalwareSim;