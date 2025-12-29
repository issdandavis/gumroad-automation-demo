import { ExternalLink } from "lucide-react";

interface ShopifyBannerProps {
  shopUrl?: string;
  className?: string;
}

export function ShopifyBanner({ 
  shopUrl = "https://aethermore-works.myshopify.com", 
  className = "" 
}: ShopifyBannerProps) {
  return (
    <div 
      className={`w-full bg-gradient-to-r from-[#96bf48] to-[#5e8e3e] py-3 px-4 ${className}`}
      data-testid="shopify-banner"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <svg 
            viewBox="0 0 109.5 124.5" 
            className="w-6 h-6 fill-white"
            aria-label="Shopify"
          >
            <path d="M74.7,14.8c0,0-1.4,0.4-3.7,1.1c-0.4-1.3-1-2.8-1.8-4.4c-2.6-5-6.5-7.7-11.1-7.7c0,0,0,0,0,0 c-0.3,0-0.6,0-1,0.1c-0.1-0.2-0.3-0.3-0.4-0.5c-2-2.2-4.6-3.2-7.7-3.1c-6,0.2-12,4.5-16.8,12.2c-3.4,5.4-6,12.2-6.7,17.5 c-6.9,2.1-11.7,3.6-11.8,3.7c-3.5,1.1-3.6,1.2-4,4.5c-0.3,2.5-9.5,73.1-9.5,73.1L72,124.5V14.6C73.2,14.7,74.7,14.8,74.7,14.8z M57.2,20.2c-4,1.2-8.4,2.6-12.7,3.9c1.2-4.7,3.6-9.4,6.4-12.5c1.1-1.1,2.6-2.4,4.3-3.2C56.9,12,57.3,16.9,57.2,20.2z M49.3,4.3 c1.4,0,2.6,0.3,3.6,0.9c-1.6,0.8-3.2,2.1-4.7,3.6c-3.8,4.1-6.7,10.5-7.9,16.6c-3.6,1.1-7.2,2.2-10.5,3.2 C31.7,19.1,39.8,4.6,49.3,4.3z M39.5,63.3c0.4,6.4,17.3,7.8,18.3,22.9c0.7,11.9-6.3,20-16.4,20.6c-12.2,0.8-18.9-6.4-18.9-6.4 l2.6-11c0,0,6.7,5.1,12.1,4.7c3.5-0.2,4.8-3.1,4.7-5.1c-0.5-8.4-14.3-7.9-15.2-21.7c-0.7-11.6,6.9-23.4,23.7-24.4 c6.5-0.4,9.8,1.2,9.8,1.2l-3.8,14.4c0,0-4.3-2-9.4-1.6C40.4,57.4,39.4,60.5,39.5,63.3z M61.3,18.9c0-3.1-0.4-7.4-1.8-11.1 c4.6,0.9,6.8,6,7.8,9.1C65,17.6,62.9,18.3,61.3,18.9z" />
            <path d="M78,123.9l21.5-5.4c0,0-9.2-62.4-9.3-63.1c-0.1-0.7-0.6-1.1-1.1-1.1c-0.5,0-9.3-0.2-9.3-0.2s-5.4-5.2-7.4-7.2 V123.9z" />
          </svg>
          <span className="text-white font-medium text-sm">
            Shop our Store
          </span>
        </div>
        <a
          href={shopUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 bg-white/20 hover:bg-white/30 text-white px-4 py-1.5 rounded-full text-sm font-medium transition-colors"
          data-testid="link-shopify-store"
        >
          Visit Store
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
}
