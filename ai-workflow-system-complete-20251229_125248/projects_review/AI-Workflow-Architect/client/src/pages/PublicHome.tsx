
/**
 * Infrastructure Update: 2025-12-29T09:27:50.260Z
 * 
 * This file has been updated as part of a comprehensive infrastructure
 * synchronization to ensure all components are versioned consistently.
 * 
 * Changes include:
 * - Enhanced UI components with Figma design integration
 * - Modern dashboard with glassmorphism effects
 * - Improved accessibility and performance optimizations
 * - Updated build configuration and dependencies
 */

import Layout from "@/components/dashboard/Layout";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Zap, Lock, Globe } from "lucide-react";
import { motion } from "framer-motion";
import bgImage from "@assets/generated_images/clean_modern_ecommerce_storefront_background.png";

export default function PublicHome() {
  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-purple-500/30">
      {/* Navigation Overlay */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 flex items-center justify-between backdrop-blur-md border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">Nex<span className="text-purple-400">Gen</span></span>
        </div>
        <div className="flex items-center gap-6">
          <a href="/shop" className="text-sm font-medium hover:text-purple-400 transition-colors">Shop</a>
          <a href="/dashboard" className="text-sm font-medium hover:text-purple-400 transition-colors flex items-center gap-2">
            <Lock className="w-3 h-3" />
            Admin Login
          </a>
          <Button className="bg-white text-black hover:bg-white/90 rounded-full px-6">
            Get Started
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <div 
          className="absolute inset-0 z-0 opacity-40"
          style={{
            backgroundImage: `url(${bgImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/50 to-black z-0" />
        
        <div className="relative z-10 max-w-4xl mx-auto text-center px-6 space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/50">
              Future-Ready Digital Solutions
            </h1>
            <p className="text-xl text-white/60 max-w-2xl mx-auto leading-relaxed">
              Powered by advanced AI agents working around the clock to deliver seamless experiences.
            </p>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button size="lg" className="h-14 px-8 rounded-full bg-purple-600 hover:bg-purple-500 text-lg shadow-[0_0_20px_rgba(147,51,234,0.4)] transition-all hover:scale-105">
              Visit Shop <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button size="lg" variant="outline" className="h-14 px-8 rounded-full border-white/20 hover:bg-white/10 text-lg backdrop-blur-sm">
              Learn More
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-6 bg-black relative">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:border-purple-500/50 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center mb-6 text-purple-400 group-hover:scale-110 transition-transform">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold mb-3">Instant Delivery</h3>
            <p className="text-white/50 leading-relaxed">Our AI swarm processes orders in real-time, ensuring zero friction from checkout to fulfillment.</p>
          </div>
          
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:border-blue-500/50 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-6 text-blue-400 group-hover:scale-110 transition-transform">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold mb-3">Secure Payments</h3>
            <p className="text-white/50 leading-relaxed">Enterprise-grade security powered by Stripe, protecting every transaction with military-grade encryption.</p>
          </div>

          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:border-green-500/50 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-green-500/20 flex items-center justify-center mb-6 text-green-400 group-hover:scale-110 transition-transform">
              <Globe className="w-6 h-6" />
            </div>
            <h3 className="text-2xl font-bold mb-3">Global Access</h3>
            <p className="text-white/50 leading-relaxed">Available worldwide with localized pricing and multi-language support out of the box.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
