import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid'; 
import { generateProjectPlan } from './services/geminiService';
import { Project, Step } from './types';
import { StepList } from './components/StepList';
import { PlusIcon, SparklesIcon, TrashIcon, TruckIcon, SettingsIcon, BoxIcon } from './components/Icons';

// Simple ID generator since we can't install uuid
const generateId = () => Math.random().toString(36).substring(2, 9);

const App = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  const [userInput, setUserInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [apiKeyMissing, setApiKeyMissing] = useState(false);

  useEffect(() => {
    if (!process.env.API_KEY) {
      setApiKeyMissing(true);
    }
  }, []);

  const createProjectFromPrompt = async (prompt: string) => {
    setIsGenerating(true);
    try {
      const plan = await generateProjectPlan(prompt);
      
      const newProject: Project = {
        id: generateId(),
        name: plan.projectName,
        description: plan.projectDescription,
        createdAt: Date.now(),
        progress: 0,
        steps: plan.steps.map(s => ({
          id: generateId(),
          title: s.title,
          description: s.description,
          category: s.category as any,
          estimatedTime: s.estimatedTime,
          isCompleted: false
        }))
      };

      setProjects(prev => [newProject, ...prev]);
      setActiveProjectId(newProject.id);
      setUserInput('');
    } catch (error) {
      console.error("Failed to generate project", error);
      alert("Something went wrong generating your plan. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || isGenerating) return;
    await createProjectFromPrompt(userInput);
  };

  const deleteProject = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setProjects(prev => prev.filter(p => p.id !== id));
    if (activeProjectId === id) setActiveProjectId(null);
  };

  const updateProject = (updatedProject: Project) => {
    setProjects(prev => prev.map(p => p.id === updatedProject.id ? updatedProject : p));
  };

  const activeProject = projects.find(p => p.id === activeProjectId);

  if (apiKeyMissing) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-800 p-4">
            <div className="max-w-md text-center">
                <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">!</span>
                </div>
                <h1 className="text-xl font-bold mb-2">Configuration Error</h1>
                <p>The <code>API_KEY</code> environment variable is missing. Please add your Google Gemini API key to the environment to use this application.</p>
            </div>
        </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white flex-shrink-0 flex flex-col border-r border-gray-800">
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
              <span className="font-bold text-white">S</span>
            </div>
            <span className="font-bold text-lg tracking-tight">ShopGuide AI</span>
          </div>
          <p className="text-xs text-gray-400">Your Personal Setup Assistant</p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Your Projects</div>
          
          {projects.length === 0 && (
            <div className="text-sm text-gray-600 px-2 italic">No projects yet.</div>
          )}

          {projects.map(project => (
            <div 
              key={project.id}
              onClick={() => setActiveProjectId(project.id)}
              className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                activeProjectId === project.id 
                  ? 'bg-green-600 text-white shadow-lg' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <div className="truncate min-w-0 pr-2">
                <div className="font-medium truncate text-sm">{project.name}</div>
                <div className={`text-xs mt-0.5 truncate ${activeProjectId === project.id ? 'text-green-200' : 'text-gray-500'}`}>
                    {project.progress}% completed
                </div>
              </div>
              <button 
                onClick={(e) => deleteProject(project.id, e)}
                className={`opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-white/20 transition-all ${activeProjectId === project.id ? 'text-white' : 'text-gray-400'}`}
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t border-gray-800">
          <button 
            onClick={() => setActiveProjectId(null)}
            className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-gray-800 hover:bg-gray-700 text-green-400 rounded-lg transition-colors font-medium text-sm"
          >
            <PlusIcon className="w-5 h-5" />
            New Project
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-white relative">
        {activeProject ? (
          <StepList 
            project={activeProject} 
            onUpdateProject={updateProject} 
          />
        ) : (
            // Empty State / Creator
          <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-4xl mx-auto w-full animate-fade-in overflow-y-auto">
            <div className="mb-6 relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-green-400 to-blue-500 rounded-full blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-xl">
                    <SparklesIcon className="w-8 h-8 text-green-500" />
                </div>
            </div>

            <h1 className="text-3xl font-extrabold text-gray-900 text-center mb-3 tracking-tight">
              Shopify Setup Copilot
            </h1>
            <p className="text-gray-500 text-center mb-8 max-w-xl leading-relaxed">
              I'm here to ensure your project completion. Type a goal below, or pick a starter mission to get detailed, AI-generated steps.
            </p>

            <form onSubmit={handleCreateProject} className="w-full max-w-2xl relative mb-12">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="e.g., I want to start selling handmade jewelry..."
                className="w-full p-4 pl-6 pr-32 text-lg rounded-2xl border-2 border-gray-200 shadow-sm focus:border-green-500 focus:ring-4 focus:ring-green-500/10 outline-none transition-all"
                disabled={isGenerating}
              />
              <button
                type="submit"
                disabled={isGenerating || !userInput.trim()}
                className={`absolute right-2.5 top-2.5 bottom-2.5 px-6 rounded-xl font-semibold text-white transition-all shadow-md flex items-center gap-2
                    ${isGenerating || !userInput.trim() 
                        ? 'bg-gray-300 cursor-not-allowed' 
                        : 'bg-green-600 hover:bg-green-700 hover:shadow-lg active:scale-95'
                    }`}
              >
                {isGenerating ? (
                    <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Thinking...</span>
                    </>
                ) : (
                    <span>Create Plan</span>
                )}
              </button>
            </form>

            <div className="w-full max-w-4xl">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4 text-center">Recommended for Beginners</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <StarterCard 
                        icon={<SettingsIcon className="w-6 h-6 text-blue-500" />}
                        title="Store Basics"
                        description="Setup name, email, & currency settings."
                        onClick={() => createProjectFromPrompt("Set up the basic configuration for a new Shopify store. This includes defining the store name, primary contact email address, and the default currency.")}
                        disabled={isGenerating}
                    />
                     <StarterCard 
                        icon={<TruckIcon className="w-6 h-6 text-orange-500" />}
                        title="Configure Shipping"
                        description="Setup domestic zones & flat rates."
                        onClick={() => createProjectFromPrompt("Configure the shipping settings for the Shopify store. Set up at least one shipping zone (e.g., domestic) with a basic flat-rate shipping option.")}
                        disabled={isGenerating}
                    />
                    <StarterCard 
                        icon={<BoxIcon className="w-6 h-6 text-purple-500" />}
                        title="Add First Product"
                        description="Draft a product with price & image."
                        onClick={() => createProjectFromPrompt("Add a sample product to the Shopify store. The product should have a title, description, price, and a placeholder image.")}
                        disabled={isGenerating}
                    />
                </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface StarterCardProps {
    icon: React.ReactNode;
    title: string;
    description: string;
    onClick: () => void;
    disabled: boolean;
}

const StarterCard: React.FC<StarterCardProps> = ({ icon, title, description, onClick, disabled }) => (
    <button 
        onClick={onClick}
        disabled={disabled}
        className="flex flex-col items-start p-5 bg-white border border-gray-200 rounded-xl hover:border-green-400 hover:shadow-lg transition-all text-left group disabled:opacity-50 disabled:cursor-not-allowed"
    >
        <div className="p-3 bg-gray-50 rounded-lg group-hover:bg-green-50 transition-colors mb-3">
            {icon}
        </div>
        <h4 className="font-bold text-gray-900 mb-1 group-hover:text-green-700 transition-colors">{title}</h4>
        <p className="text-sm text-gray-500 leading-snug">{description}</p>
    </button>
);

export default App;