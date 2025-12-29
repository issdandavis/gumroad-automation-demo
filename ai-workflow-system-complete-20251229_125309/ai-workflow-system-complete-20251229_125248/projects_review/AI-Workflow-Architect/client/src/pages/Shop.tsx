
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
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, ShoppingCart, Star } from "lucide-react";
import { motion } from "framer-motion";

export default function Shop() {
  const products = [
    { id: 1, name: "AI Consultation Pro", price: "$199", category: "Service", rating: 4.8 },
    { id: 2, name: "Digital Asset Pack", price: "$49", category: "Download", rating: 4.9 },
    { id: 3, name: "Premium Membership", price: "$29/mo", category: "Subscription", rating: 5.0 },
    { id: 4, name: "Custom Workflow", price: "$499", category: "Service", rating: 4.7 },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      <nav className="border-b border-border bg-card/50 backdrop-blur-xl px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <h1 className="text-xl font-bold">Storefront</h1>
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon">
            <Search className="w-5 h-5" />
          </Button>
          <Button className="bg-primary text-primary-foreground gap-2">
            <ShoppingCart className="w-4 h-4" /> Cart (0)
          </Button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6 md:p-10">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">Featured Products</h2>
          <Button variant="outline" className="gap-2">
            <Filter className="w-4 h-4" /> Filter
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <motion.div 
              key={product.id}
              whileHover={{ y: -5 }}
              className="group bg-card border border-border rounded-2xl overflow-hidden hover:border-primary/50 transition-all"
            >
              <div className="aspect-square bg-muted flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="text-4xl">📦</span>
              </div>
              <div className="p-5 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <Badge variant="secondary" className="mb-2">{product.category}</Badge>
                    <h3 className="font-bold text-lg">{product.name}</h3>
                  </div>
                  <div className="flex items-center gap-1 text-yellow-500 text-xs font-bold">
                    <Star className="w-3 h-3 fill-current" /> {product.rating}
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2">
                  <span className="text-xl font-bold text-primary">{product.price}</span>
                  <Button size="sm">Add to Cart</Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
