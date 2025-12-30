#!/usr/bin/env python3
"""
Self-Evolving AI Web Interface
=============================

Modern web dashboard for monitoring and controlling the self-evolving AI system.
Built with Flask and real-time updates for a professional user experience.

Features:
- Real-time system status dashboard
- Interactive mutation management
- Fitness metrics visualization
- Storage sync monitoring
- Tutorial integration
- API endpoints for external integration

Usage:
    python web_interface.py [--port 5000] [--debug]
    
Then visit: http://localhost:5000

API Endpoints:
    GET  /api/status          - System status
    POST /api/mutate          - Propose mutation
    GET  /api/fitness         - Fitness metrics
    POST /api/rollback        - Rollback system
    GET  /api/tutorials       - Available tutorials
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time

from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import Mutation, MutationType
from tutorial_system import TutorialSystem

# Import bridge integration if available
try:
    from bridge_integration import BridgeIntegration, create_bridge_integration
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False


class WebInterface:
    """
    Web interface for the Self-Evolving AI Framework.
    
    Provides a modern, responsive dashboard for monitoring and controlling
    the AI system with real-time updates and interactive features.
    """
    
    def __init__(self, port: int = 5000, debug: bool = False):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'demo-secret-key-change-in-production'
        CORS(self.app)  # Enable CORS for API access
        
        self.port = port
        self.debug = debug
        self.framework = None
        self.tutorial_system = TutorialSystem()
        self.bridge_integration = None
        
        # Initialize framework in background
        self._init_framework()
        
        # Initialize bridge integration if available
        if BRIDGE_AVAILABLE:
            self._init_bridge_integration()
        
        # Setup routes
        self._setup_routes()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _init_framework(self):
        """Initialize the AI framework"""
        try:
            self.framework = EvolvingAIFramework()
            success = self.framework.initialize()
            if success:
                print("✅ Framework initialized for web interface")
            else:
                print("❌ Framework initialization failed")
        except Exception as e:
            print(f"❌ Framework error: {e}")
    
    def _init_bridge_integration(self):
        """Initialize bridge integration asynchronously"""
        def init_bridge():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.bridge_integration = loop.run_until_complete(create_bridge_integration())
                print("✅ Bridge integration initialized for web interface")
            except Exception as e:
                print(f"⚠️ Bridge integration failed: {e}")
                self.bridge_integration = None
        
        # Run bridge initialization in a separate thread
        bridge_thread = threading.Thread(target=init_bridge, daemon=True)
        bridge_thread.start()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template_string(self._get_dashboard_template())
        
        @self.app.route('/tutorials')
        def tutorials_page():
            """Tutorials page"""
            return render_template_string(self._get_tutorials_template())
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            if not self.framework:
                return jsonify({"error": "Framework not initialized"}), 500
            
            try:
                status = self.framework.get_status()
                
                # Add bridge integration status if available
                if self.bridge_integration:
                    status['bridge'] = {
                        'connected': self.bridge_integration.connected,
                        'last_health_check': self.bridge_integration.last_health_check.isoformat() if self.bridge_integration.last_health_check else None
                    }
                else:
                    status['bridge'] = {'connected': False, 'available': BRIDGE_AVAILABLE}
                
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/unified-status')
        def api_unified_status():
            """Get unified system status from Bridge API"""
            if not self.bridge_integration:
                return jsonify({"error": "Bridge integration not available"}), 503
            
            try:
                # This would need to be implemented as an async endpoint in a real app
                # For now, return local status with bridge info
                status = self.framework.get_status() if self.framework else {}
                status['unified'] = True
                status['bridge_connected'] = self.bridge_integration.connected
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/mutate', methods=['POST'])
        def api_mutate():
            """Propose a mutation"""
            if not self.framework:
                return jsonify({"error": "Framework not initialized"}), 500
            
            try:
                data = request.get_json()
                mutation = Mutation(
                    type=data.get('type'),
                    description=data.get('description'),
                    fitness_impact=float(data.get('fitness_impact', 0)),
                    source_ai=data.get('source_ai', 'WebUI')
                )
                
                result = self.framework.propose_mutation(mutation)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/fitness')
        def api_fitness():
            """Get fitness metrics"""
            if not self.framework:
                return jsonify({"error": "Framework not initialized"}), 500
            
            try:
                fitness = self.framework.get_fitness()
                return jsonify(fitness.to_dict())
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/rollback', methods=['POST'])
        def api_rollback():
            """Rollback to snapshot"""
            if not self.framework:
                return jsonify({"error": "Framework not initialized"}), 500
            
            try:
                data = request.get_json()
                snapshot_id = data.get('snapshot_id')
                result = self.framework.rollback_to(snapshot_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/tutorials')
        def api_tutorials():
            """Get available tutorials"""
            tutorials = [
                {
                    "name": "getting_started",
                    "title": "Getting Started",
                    "description": "Basic framework introduction and demo",
                    "duration": "10 minutes",
                    "difficulty": "Beginner"
                },
                {
                    "name": "mutations",
                    "title": "Mastering Mutations", 
                    "description": "Understanding and applying system mutations",
                    "duration": "15 minutes",
                    "difficulty": "Intermediate"
                },
                {
                    "name": "fitness",
                    "title": "Fitness Monitoring",
                    "description": "Performance optimization and metrics",
                    "duration": "12 minutes", 
                    "difficulty": "Intermediate"
                },
                {
                    "name": "autonomy",
                    "title": "Autonomous Operation",
                    "description": "Self-managing AI workflows",
                    "duration": "20 minutes",
                    "difficulty": "Advanced"
                }
            ]
            return jsonify(tutorials)
        
        @self.app.route('/api/demo-data')
        def api_demo_data():
            """Get demo data for testing"""
            return jsonify({
                "sample_mutations": [
                    {
                        "type": "communication_enhancement",
                        "description": "Add WebSocket real-time communication",
                        "fitness_impact": 5.0
                    },
                    {
                        "type": "intelligence_upgrade",
                        "description": "Integrate Claude 3.5 Sonnet",
                        "fitness_impact": 8.0
                    },
                    {
                        "type": "storage_optimization", 
                        "description": "Implement Redis caching layer",
                        "fitness_impact": 3.0
                    }
                ],
                "demo_secrets": self.tutorial_system.demo_secrets
            })
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        def monitor_system():
            """Background system monitoring"""
            while True:
                try:
                    if self.framework:
                        # Update fitness metrics
                        fitness = self.framework.get_fitness()
                        # Could emit WebSocket events here for real-time updates
                except Exception as e:
                    print(f"Background monitoring error: {e}")
                time.sleep(30)  # Update every 30 seconds
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def _get_dashboard_template(self) -> str:
        """Get the main dashboard HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Self-Evolving AI Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover:hover { transform: translateY(-2px); transition: all 0.3s ease; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg">
        <div class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold">🧬 Self-Evolving AI</h1>
                    <p class="text-blue-100">Autonomous AI System Dashboard</p>
                </div>
                <div class="flex space-x-4">
                    <button onclick="refreshData()" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition">
                        🔄 Refresh
                    </button>
                    <a href="/tutorials" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition">
                        📚 Tutorials
                    </a>
                </div>
            </div>
        </div>
    </header>

    <div class="container mx-auto px-6 py-8">
        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-green-100 text-green-600">
                        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">System Status</p>
                        <p class="text-lg font-semibold" id="system-status">Loading...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-blue-100 text-blue-600">
                        <span class="text-xl">🧬</span>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Generation</p>
                        <p class="text-lg font-semibold" id="generation">Loading...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-purple-100 text-purple-600">
                        <span class="text-xl">💪</span>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Fitness Score</p>
                        <p class="text-lg font-semibold" id="fitness-score">Loading...</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-md p-6 card-hover">
                <div class="flex items-center">
                    <div class="p-3 rounded-full bg-yellow-100 text-yellow-600">
                        <span class="text-xl">🔄</span>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm text-gray-600">Mutations</p>
                        <p class="text-lg font-semibold" id="mutations-count">Loading...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Mutation Control -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4">🧬 Propose Mutation</h2>
                <form id="mutation-form" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Mutation Type</label>
                        <select id="mutation-type" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                            <option value="communication_enhancement">Communication Enhancement</option>
                            <option value="intelligence_upgrade">Intelligence Upgrade</option>
                            <option value="storage_optimization">Storage Optimization</option>
                            <option value="language_expansion">Language Expansion</option>
                            <option value="protocol_improvement">Protocol Improvement</option>
                            <option value="autonomy_adjustment">Autonomy Adjustment</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                        <textarea id="mutation-description" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Describe the mutation..."></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Fitness Impact</label>
                        <input type="number" id="mutation-impact" step="0.1" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="5.0">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition">
                        Apply Mutation
                    </button>
                </form>
                <div id="mutation-result" class="mt-4"></div>
            </div>

            <!-- Fitness Chart -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4">📈 Fitness Trends</h2>
                <canvas id="fitness-chart" width="400" height="200"></canvas>
            </div>

            <!-- System Logs -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4">📋 Recent Activity</h2>
                <div id="activity-log" class="space-y-2 max-h-64 overflow-y-auto">
                    <div class="text-gray-500">Loading activity...</div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4">⚡ Quick Actions</h2>
                <div class="grid grid-cols-2 gap-4">
                    <button onclick="runDemo()" class="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg transition">
                        🎬 Run Demo
                    </button>
                    <button onclick="syncStorage()" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition">
                        💾 Sync Storage
                    </button>
                    <button onclick="showTutorials()" class="bg-purple-500 hover:bg-purple-600 text-white font-bold py-3 px-4 rounded-lg transition">
                        📚 Tutorials
                    </button>
                    <button onclick="exportData()" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-3 px-4 rounded-lg transition">
                        📤 Export Data
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let fitnessChart;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            initFitnessChart();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });

        // Refresh all data
        async function refreshData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateStatusCards(data);
                updateActivityLog(data);
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        // Update status cards
        function updateStatusCards(data) {
            document.getElementById('system-status').textContent = data.running ? 'Running' : 'Stopped';
            document.getElementById('generation').textContent = data.dna?.generation || 'N/A';
            document.getElementById('fitness-score').textContent = data.dna?.fitness_score?.toFixed(1) || 'N/A';
            document.getElementById('mutations-count').textContent = data.dna?.mutations_count || '0';
        }

        // Update activity log
        function updateActivityLog(data) {
            const log = document.getElementById('activity-log');
            const activities = [
                `System initialized at ${new Date().toLocaleTimeString()}`,
                `Generation ${data.dna?.generation || 'N/A'} - Fitness: ${data.dna?.fitness_score?.toFixed(1) || 'N/A'}`,
                `Storage platforms: ${Object.keys(data.storage?.platforms || {}).length} configured`,
                `Autonomy level: ${((data.dna?.core_traits?.autonomy_level || 0) * 100).toFixed(0)}%`
            ];
            
            log.innerHTML = activities.map(activity => 
                `<div class="text-sm text-gray-600 p-2 bg-gray-50 rounded">${activity}</div>`
            ).join('');
        }

        // Initialize fitness chart
        function initFitnessChart() {
            const ctx = document.getElementById('fitness-chart').getContext('2d');
            fitnessChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6', 'Gen 7'],
                    datasets: [{
                        label: 'Fitness Score',
                        data: [100, 102, 105, 108, 110, 113, 118],
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }

        // Handle mutation form
        document.getElementById('mutation-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const mutation = {
                type: document.getElementById('mutation-type').value,
                description: document.getElementById('mutation-description').value,
                fitness_impact: parseFloat(document.getElementById('mutation-impact').value) || 0,
                source_ai: 'WebUI'
            };
            
            try {
                const response = await fetch('/api/mutate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(mutation)
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('mutation-result');
                
                if (result.approved) {
                    resultDiv.innerHTML = `<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                        ✅ Mutation approved and applied!
                    </div>`;
                    refreshData(); // Refresh dashboard
                } else {
                    resultDiv.innerHTML = `<div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
                        ⏳ Mutation queued for approval (Risk: ${(result.risk || 0).toFixed(3)})
                    </div>`;
                }
            } catch (error) {
                document.getElementById('mutation-result').innerHTML = `<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    ❌ Error: ${error.message}
                </div>`;
            }
        });

        // Quick action functions
        function runDemo() {
            alert('Demo functionality - would run system demonstration');
        }

        function syncStorage() {
            alert('Storage sync functionality - would sync to all platforms');
        }

        function showTutorials() {
            window.location.href = '/tutorials';
        }

        function exportData() {
            alert('Export functionality - would download system data');
        }
    </script>
</body>
</html>
        """
    
    def _get_tutorials_template(self) -> str:
        """Get the tutorials page HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Framework Tutorials</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <header class="bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold">📚 AI Framework Tutorials</h1>
                    <p class="text-blue-100">Learn to master the self-evolving AI system</p>
                </div>
                <a href="/" class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition">
                    ← Back to Dashboard
                </a>
            </div>
        </div>
    </header>

    <div class="container mx-auto px-6 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="tutorials-grid">
            <!-- Tutorials will be loaded here -->
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadTutorials();
        });

        async function loadTutorials() {
            try {
                const response = await fetch('/api/tutorials');
                const tutorials = await response.json();
                
                const grid = document.getElementById('tutorials-grid');
                grid.innerHTML = tutorials.map(tutorial => `
                    <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                        <div class="flex items-center mb-4">
                            <span class="text-2xl mr-3">📖</span>
                            <div>
                                <h3 class="text-lg font-bold">${tutorial.title}</h3>
                                <p class="text-sm text-gray-500">${tutorial.duration} • ${tutorial.difficulty}</p>
                            </div>
                        </div>
                        <p class="text-gray-600 mb-4">${tutorial.description}</p>
                        <button onclick="startTutorial('${tutorial.name}')" 
                                class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition">
                            Start Tutorial
                        </button>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading tutorials:', error);
            }
        }

        function startTutorial(name) {
            alert(`Starting tutorial: ${name}\\n\\nIn a real implementation, this would:\\n• Open an interactive tutorial\\n• Guide through step-by-step instructions\\n• Provide hands-on practice\\n\\nFor now, run: python tutorial_system.py ${name}`);
        }
    </script>
</body>
</html>
        """
    
    def run(self):
        """Start the web interface"""
        print(f"""
🌐 Starting Self-Evolving AI Web Interface...

Dashboard: http://localhost:{self.port}
API Docs:  http://localhost:{self.port}/api/status

Features:
✅ Real-time system monitoring
✅ Interactive mutation management  
✅ Fitness visualization
✅ Tutorial integration
✅ RESTful API endpoints

Press Ctrl+C to stop
        """)
        
        self.app.run(host='0.0.0.0', port=self.port, debug=self.debug)


def main():
    """Main web interface entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Evolving AI Web Interface")
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    web_interface = WebInterface(port=args.port, debug=args.debug)
    web_interface.run()


if __name__ == "__main__":
    main()