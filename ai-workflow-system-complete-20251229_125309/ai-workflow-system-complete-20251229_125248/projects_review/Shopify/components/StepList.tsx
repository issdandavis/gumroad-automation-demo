import React, { useState } from 'react';
import { Project, Step, StepAdvice } from '../types';
import { CheckCircleIcon, ChevronRightIcon, InfoIcon, SparklesIcon } from './Icons';
import { getStepDetails } from '../services/geminiService';

interface StepListProps {
  project: Project;
  onUpdateProject: (updatedProject: Project) => void;
}

export const StepList: React.FC<StepListProps> = ({ project, onUpdateProject }) => {
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [loadingAdviceId, setLoadingAdviceId] = useState<string | null>(null);
  const [adviceCache, setAdviceCache] = useState<Record<string, StepAdvice>>({});

  const toggleStep = (stepId: string) => {
    const updatedSteps = project.steps.map(s => 
      s.id === stepId ? { ...s, isCompleted: !s.isCompleted } : s
    );
    const completedCount = updatedSteps.filter(s => s.isCompleted).length;
    const progress = Math.round((completedCount / updatedSteps.length) * 100);

    onUpdateProject({
      ...project,
      steps: updatedSteps,
      progress
    });
  };

  const handleGetAdvice = async (step: Step) => {
    if (selectedStepId === step.id) {
      setSelectedStepId(null);
      return;
    }
    
    setSelectedStepId(step.id);

    if (adviceCache[step.id]) return;

    setLoadingAdviceId(step.id);
    try {
      const advice = await getStepDetails(step.title, project.description);
      setAdviceCache(prev => ({ ...prev, [step.id]: advice }));
    } catch (error) {
      console.error("Failed to get advice", error);
    } finally {
      setLoadingAdviceId(null);
    }
  };

  const currentAdvice = selectedStepId ? adviceCache[selectedStepId] : null;

  return (
    <div className="flex flex-col md:flex-row h-full overflow-hidden">
      {/* List Section */}
      <div className={`flex-1 overflow-y-auto p-6 ${selectedStepId ? 'hidden md:block' : ''}`}>
        <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">{project.name}</h2>
            <p className="text-gray-500 mt-1">{project.description}</p>
            
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-green-600 h-2.5 rounded-full transition-all duration-500 ease-out" 
                style={{ width: `${project.progress}%` }}
              ></div>
            </div>
            <p className="text-right text-xs text-green-700 font-medium mt-1">{project.progress}% Complete</p>
        </div>

        <div className="space-y-3">
          {project.steps.map((step) => (
            <div 
              key={step.id} 
              className={`group bg-white rounded-lg border transition-all duration-200 
                ${step.isCompleted ? 'border-green-200 bg-green-50/50' : 'border-gray-200 hover:border-green-400 hover:shadow-md'}
                ${selectedStepId === step.id ? 'ring-2 ring-green-500 border-transparent' : ''}
              `}
            >
              <div className="p-4 flex items-center gap-4">
                <button 
                  onClick={() => toggleStep(step.id)}
                  className={`flex-shrink-0 transition-colors ${step.isCompleted ? 'text-green-600' : 'text-gray-300 hover:text-green-500'}`}
                >
                  <CheckCircleIcon className="w-8 h-8" checked={step.isCompleted} />
                </button>
                
                <div className="flex-1 min-w-0" onClick={() => handleGetAdvice(step)}>
                  <h3 className={`font-semibold truncate cursor-pointer ${step.isCompleted ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                    {step.title}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs font-medium px-2 py-0.5 rounded bg-gray-100 text-gray-600 uppercase tracking-wide">
                        {step.category}
                    </span>
                    <span className="text-xs text-gray-400">
                        {step.estimatedTime}
                    </span>
                  </div>
                </div>

                <button 
                  onClick={() => handleGetAdvice(step)}
                  className="p-2 rounded-full hover:bg-gray-100 text-gray-400 hover:text-green-600 transition-colors"
                >
                  <ChevronRightIcon />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Details Panel */}
      {selectedStepId && (
        <div className="w-full md:w-[450px] bg-white border-l border-gray-200 shadow-xl overflow-y-auto flex flex-col h-full absolute inset-0 md:static z-20">
             <div className="p-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white z-10">
                <h3 className="font-bold text-gray-800">Step Guide</h3>
                <button 
                    onClick={() => setSelectedStepId(null)}
                    className="md:hidden text-sm text-gray-500 hover:text-gray-900"
                >
                    Close
                </button>
            </div>

            <div className="p-6">
                {loadingAdviceId === selectedStepId ? (
                    <div className="flex flex-col items-center justify-center h-64 space-y-4 animate-pulse">
                        <SparklesIcon className="w-10 h-10 text-green-400 animate-spin" />
                        <p className="text-gray-500 text-sm">AI is writing your guide...</p>
                    </div>
                ) : currentAdvice ? (
                    <div className="space-y-8 animate-fade-in">
                        
                        {/* Why it matters */}
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                            <div className="flex items-start gap-3">
                                <InfoIcon className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                                <div>
                                    <h4 className="text-sm font-bold text-blue-800 mb-1">Why this matters</h4>
                                    <p className="text-sm text-blue-700 leading-relaxed">
                                        {currentAdvice.whyItMatters}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Instructions */}
                        <div>
                            <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <span className="bg-green-100 text-green-700 w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span>
                                Action Plan
                            </h4>
                            <div className="prose prose-sm prose-green text-gray-600">
                                <div dangerouslySetInnerHTML={{ 
                                    // Simple markdown parser for bolding
                                    __html: currentAdvice.detailedInstructions.replace(/\*\*(.*?)\*\*/g, '<strong class="text-gray-900 font-semibold">$1</strong>').replace(/\n/g, '<br />') 
                                }} />
                            </div>
                        </div>

                        {/* Pitfalls */}
                        <div>
                            <h4 className="text-sm font-bold text-red-800 uppercase tracking-wide mb-3">Avoid these mistakes</h4>
                            <ul className="space-y-2">
                                {currentAdvice.commonPitfalls.map((pitfall, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                                        <span className="text-red-500 mt-1">×</span>
                                        {pitfall}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                ) : null}
            </div>
            
            <div className="mt-auto p-4 border-t border-gray-100 bg-gray-50">
                <button 
                    onClick={() => {
                        toggleStep(selectedStepId);
                        setSelectedStepId(null);
                    }}
                    className="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg shadow-sm transition-all"
                >
                    Mark as Done
                </button>
            </div>
        </div>
      )}
    </div>
  );
};