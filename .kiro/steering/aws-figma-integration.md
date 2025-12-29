---
inclusion: manual
---

# AWS + Figma Integration Configuration

## Overview

This guide configures the Figma power to work seamlessly with AWS infrastructure for the AI Workflow Architect platform, including S3 asset storage, CloudFront CDN, and Lambda@Edge optimizations.

## AWS Services Setup

### 1. S3 Bucket Configuration

**Bucket Structure**:
```
ai-workflow-assets/
├── figma-exports/
│   ├── components/
│   ├── icons/
│   ├── images/
│   └── prototypes/
├── generated-assets/
│   ├── optimized-images/
│   ├── webp-variants/
│   └── thumbnails/
└── design-tokens/
    ├── colors.json
    ├── typography.json
    └── spacing.json
```

**Bucket Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ai-workflow-assets/*",
      "Condition": {
        "StringEquals": {
          "aws:Referer": [
            "https://aiworkflow.com/*",
            "https://*.aiworkflow.com/*"
          ]
        }
      }
    }
  ]
}
```

### 2. CloudFront Distribution

**Distribution Configuration**:
```yaml
# cloudfront-config.yml
Distribution:
  DistributionConfig:
    Origins:
      - Id: S3-ai-workflow-assets
        DomainName: ai-workflow-assets.s3.amazonaws.com
        S3OriginConfig:
          OriginAccessIdentity: origin-access-identity/cloudfront/ABCDEFG1234567
    
    DefaultCacheBehavior:
      TargetOriginId: S3-ai-workflow-assets
      ViewerProtocolPolicy: redirect-to-https
      CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # Managed-CachingOptimized
      
    CacheBehaviors:
      - PathPattern: "/figma-exports/*"
        TargetOriginId: S3-ai-workflow-assets
        ViewerProtocolPolicy: redirect-to-https
        CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad
        TTL: 31536000  # 1 year for Figma assets
        
      - PathPattern: "/generated-assets/*"
        TargetOriginId: S3-ai-workflow-assets
        ViewerProtocolPolicy: redirect-to-https
        CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad
        TTL: 86400     # 1 day for generated content
```

### 3. Lambda@Edge Functions

**Image Optimization Function**:
```javascript
// lambda-edge-image-optimization.js
exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  const headers = request.headers;
  
  // Check if WebP is supported
  const acceptHeader = headers.accept && headers.accept[0] ? headers.accept[0].value : '';
  const supportsWebP = acceptHeader.includes('image/webp');
  
  // Modify request for WebP variants
  if (supportsWebP && request.uri.match(/\.(jpg|jpeg|png)$/i)) {
    const webpUri = request.uri.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    request.uri = webpUri;
  }
  
  return request;
};
```

## Environment Configuration

### Development Environment
```bash
# .env.development
NODE_ENV=development
VITE_AWS_REGION=us-east-1
VITE_AWS_S3_BUCKET=ai-workflow-assets-dev
VITE_AWS_CLOUDFRONT_DOMAIN=https://dev-assets.aiworkflow.com
VITE_FIGMA_CDN_BASE=https://dev-assets.aiworkflow.com/figma-exports

# Figma API Configuration
FIGMA_ACCESS_TOKEN=your_figma_token
FIGMA_TEAM_ID=your_team_id
FIGMA_WEBHOOK_SECRET=your_webhook_secret
```

### Production Environment
```bash
# .env.production
NODE_ENV=production
VITE_AWS_REGION=us-east-1
VITE_AWS_S3_BUCKET=ai-workflow-assets
VITE_AWS_CLOUDFRONT_DOMAIN=https://assets.aiworkflow.com
VITE_FIGMA_CDN_BASE=https://assets.aiworkflow.com/figma-exports

# Production Figma Configuration
FIGMA_ACCESS_TOKEN=prod_figma_token
FIGMA_TEAM_ID=prod_team_id
FIGMA_WEBHOOK_SECRET=prod_webhook_secret
```

## Asset Pipeline Integration

### 1. Figma Asset Processor

```typescript
// server/services/figmaAssetProcessor.ts
import AWS from 'aws-sdk';
import sharp from 'sharp';

const s3 = new AWS.S3({
  region: process.env.AWS_REGION,
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});

export class FigmaAssetProcessor {
  async processAndUploadAsset(
    figmaUrl: string, 
    nodeId: string, 
    assetType: 'image' | 'icon' | 'component'
  ) {
    try {
      // 1. Get asset from Figma
      const figmaAsset = await this.getFigmaAsset(figmaUrl, nodeId);
      
      // 2. Optimize for web
      const optimizedAssets = await this.optimizeAsset(figmaAsset, assetType);
      
      // 3. Upload to S3
      const uploadPromises = optimizedAssets.map(asset => 
        this.uploadToS3(asset, assetType)
      );
      
      const uploadResults = await Promise.all(uploadPromises);
      
      // 4. Invalidate CloudFront cache
      await this.invalidateCloudFrontCache(uploadResults.map(r => r.key));
      
      return uploadResults;
    } catch (error) {
      console.error('Asset processing failed:', error);
      throw error;
    }
  }

  private async optimizeAsset(buffer: Buffer, type: string) {
    const optimizations = [];
    
    // Original format
    optimizations.push({
      buffer,
      format: 'original',
      suffix: ''
    });
    
    // WebP variant for better compression
    const webpBuffer = await sharp(buffer)
      .webp({ quality: 85 })
      .toBuffer();
    
    optimizations.push({
      buffer: webpBuffer,
      format: 'webp',
      suffix: '.webp'
    });
    
    // Thumbnail for previews
    if (type === 'image') {
      const thumbnailBuffer = await sharp(buffer)
        .resize(300, 300, { fit: 'inside' })
        .webp({ quality: 80 })
        .toBuffer();
      
      optimizations.push({
        buffer: thumbnailBuffer,
        format: 'thumbnail',
        suffix: '_thumb.webp'
      });
    }
    
    return optimizations;
  }

  private async uploadToS3(asset: any, type: string) {
    const key = `figma-exports/${type}s/${Date.now()}${asset.suffix}`;
    
    const uploadParams = {
      Bucket: process.env.AWS_S3_BUCKET!,
      Key: key,
      Body: asset.buffer,
      ContentType: this.getContentType(asset.format),
      CacheControl: 'public, max-age=31536000', // 1 year
      Metadata: {
        'figma-processed': 'true',
        'optimization-level': asset.format
      }
    };
    
    const result = await s3.upload(uploadParams).promise();
    return { key, url: result.Location, format: asset.format };
  }

  private async invalidateCloudFrontCache(keys: string[]) {
    const cloudfront = new AWS.CloudFront();
    
    const params = {
      DistributionId: process.env.AWS_CLOUDFRONT_DISTRIBUTION_ID!,
      InvalidationBatch: {
        CallerReference: `figma-${Date.now()}`,
        Paths: {
          Quantity: keys.length,
          Items: keys.map(key => `/${key}`)
        }
      }
    };
    
    return cloudfront.createInvalidation(params).promise();
  }
}
```

### 2. Vite Plugin for Asset Integration

```typescript
// vite-plugin-figma-assets.ts
import { Plugin } from 'vite';
import { FigmaAssetProcessor } from './server/services/figmaAssetProcessor';

export function figmaAssetsPlugin(): Plugin {
  const processor = new FigmaAssetProcessor();
  
  return {
    name: 'figma-assets',
    configureServer(server) {
      server.middlewares.use('/api/figma-assets', async (req, res, next) => {
        if (req.method === 'POST') {
          try {
            const { figmaUrl, nodeId, assetType } = req.body;
            const results = await processor.processAndUploadAsset(figmaUrl, nodeId, assetType);
            
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ success: true, assets: results }));
          } catch (error) {
            res.statusCode = 500;
            res.end(JSON.stringify({ error: error.message }));
          }
        } else {
          next();
        }
      });
    },
    
    generateBundle(options, bundle) {
      // Process Figma assets during build
      Object.keys(bundle).forEach(fileName => {
        const chunk = bundle[fileName];
        if (chunk.type === 'asset' && chunk.source) {
          // Upload static assets to S3 during build
          this.processStaticAsset(chunk, fileName);
        }
      });
    }
  };
}
```

## Figma Webhook Integration

### 1. Webhook Handler

```typescript
// server/routes/figmaWebhooks.ts
import express from 'express';
import crypto from 'crypto';
import { FigmaAssetProcessor } from '../services/figmaAssetProcessor';

const router = express.Router();
const processor = new FigmaAssetProcessor();

// Verify Figma webhook signature
function verifyFigmaSignature(req: express.Request): boolean {
  const signature = req.headers['x-figma-signature'] as string;
  const body = JSON.stringify(req.body);
  
  const expectedSignature = crypto
    .createHmac('sha256', process.env.FIGMA_WEBHOOK_SECRET!)
    .update(body)
    .digest('hex');
  
  return signature === expectedSignature;
}

router.post('/figma-webhook', async (req, res) => {
  if (!verifyFigmaSignature(req)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  const { event_type, file_key, triggered_by } = req.body;
  
  try {
    switch (event_type) {
      case 'FILE_UPDATE':
        // Process updated Figma file
        await processor.processFileUpdate(file_key);
        break;
        
      case 'FILE_VERSION_UPDATE':
        // Handle version changes
        await processor.processVersionUpdate(file_key, req.body.version_id);
        break;
        
      case 'FILE_COMMENT':
        // Process design feedback
        await processor.processComment(file_key, req.body.comment);
        break;
    }
    
    res.json({ success: true });
  } catch (error) {
    console.error('Webhook processing failed:', error);
    res.status(500).json({ error: 'Processing failed' });
  }
});

export default router;
```

### 2. Real-time Design Sync

```typescript
// client/src/hooks/useFigmaSync.ts
import { useEffect, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';

export function useFigmaSync(fileKey: string) {
  const [isConnected, setIsConnected] = useState(false);
  const queryClient = useQueryClient();
  
  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(`wss://api.aiworkflow.com/figma-sync/${fileKey}`);
    
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      switch (update.type) {
        case 'DESIGN_UPDATE':
          // Invalidate and refetch design data
          queryClient.invalidateQueries(['figma-design', fileKey]);
          break;
          
        case 'ASSET_PROCESSED':
          // Update asset URLs
          queryClient.setQueryData(['figma-assets', fileKey], (old: any) => ({
            ...old,
            assets: [...(old?.assets || []), update.asset]
          }));
          break;
      }
    };
    
    return () => ws.close();
  }, [fileKey, queryClient]);
  
  return { isConnected };
}
```

## Performance Optimization

### 1. Asset Preloading Strategy

```typescript
// client/src/lib/assetPreloader.ts
export class FigmaAssetPreloader {
  private cache = new Map<string, Promise<string>>();
  
  async preloadAsset(assetUrl: string): Promise<string> {
    if (this.cache.has(assetUrl)) {
      return this.cache.get(assetUrl)!;
    }
    
    const promise = this.loadAsset(assetUrl);
    this.cache.set(assetUrl, promise);
    
    return promise;
  }
  
  private async loadAsset(url: string): Promise<string> {
    // Check if WebP is supported
    const supportsWebP = await this.checkWebPSupport();
    
    // Use WebP variant if available and supported
    const optimizedUrl = supportsWebP ? url.replace(/\.(jpg|jpeg|png)$/, '.webp') : url;
    
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(optimizedUrl);
      img.onerror = () => {
        // Fallback to original format
        if (optimizedUrl !== url) {
          const fallbackImg = new Image();
          fallbackImg.onload = () => resolve(url);
          fallbackImg.onerror = reject;
          fallbackImg.src = url;
        } else {
          reject(new Error(`Failed to load asset: ${url}`));
        }
      };
      img.src = optimizedUrl;
    });
  }
  
  private async checkWebPSupport(): Promise<boolean> {
    return new Promise((resolve) => {
      const webP = new Image();
      webP.onload = webP.onerror = () => resolve(webP.height === 2);
      webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
    });
  }
}
```

### 2. Intelligent Caching

```typescript
// client/src/lib/figmaCache.ts
export class FigmaCache {
  private static instance: FigmaCache;
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  
  static getInstance(): FigmaCache {
    if (!FigmaCache.instance) {
      FigmaCache.instance = new FigmaCache();
    }
    return FigmaCache.instance;
  }
  
  set(key: string, data: any, ttl: number = 3600000): void { // 1 hour default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }
  
  get(key: string): any | null {
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }
  
  invalidate(pattern: string): void {
    const regex = new RegExp(pattern);
    
    for (const [key] of this.cache) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }
}
```

## Monitoring and Analytics

### 1. CloudWatch Metrics

```typescript
// server/middleware/figmaMetrics.ts
import AWS from 'aws-sdk';

const cloudwatch = new AWS.CloudWatch({ region: process.env.AWS_REGION });

export function trackFigmaMetrics() {
  return async (req: any, res: any, next: any) => {
    const startTime = Date.now();
    
    res.on('finish', async () => {
      const duration = Date.now() - startTime;
      
      const params = {
        Namespace: 'AIWorkflow/Figma',
        MetricData: [
          {
            MetricName: 'RequestDuration',
            Value: duration,
            Unit: 'Milliseconds',
            Dimensions: [
              {
                Name: 'Endpoint',
                Value: req.path
              },
              {
                Name: 'StatusCode',
                Value: res.statusCode.toString()
              }
            ]
          }
        ]
      };
      
      try {
        await cloudwatch.putMetricData(params).promise();
      } catch (error) {
        console.error('Failed to send metrics:', error);
      }
    });
    
    next();
  };
}
```

### 2. Error Tracking

```typescript
// server/services/figmaErrorTracker.ts
export class FigmaErrorTracker {
  static async trackError(error: Error, context: any) {
    const errorData = {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString(),
      service: 'figma-integration'
    };
    
    // Send to CloudWatch Logs
    console.error('Figma Integration Error:', errorData);
    
    // Send to external monitoring (optional)
    if (process.env.ERROR_TRACKING_ENDPOINT) {
      try {
        await fetch(process.env.ERROR_TRACKING_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(errorData)
        });
      } catch (trackingError) {
        console.error('Failed to send error to tracking service:', trackingError);
      }
    }
  }
}
```

This AWS integration ensures your Figma power works seamlessly with cloud infrastructure while maintaining high performance, reliability, and scalability for the AI Workflow Architect platform.