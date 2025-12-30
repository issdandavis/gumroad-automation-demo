/**
 * Unified Logging Service for Bridge API
 */

import winston from 'winston';
import { unifiedConfig } from '../config';

export class Logger {
  private logger: winston.Logger;
  private context: string;

  constructor(context: string = 'BridgeAPI') {
    this.context = context;
    this.logger = winston.createLogger({
      level: unifiedConfig.shared.monitoring.logLevel,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
        winston.format.printf(({ timestamp, level, message, context, ...meta }) => {
          return JSON.stringify({
            timestamp,
            level,
            context: context || this.context,
            message,
            ...meta
          });
        })
      ),
      defaultMeta: { service: 'bridge-api', context: this.context },
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple(),
            winston.format.printf(({ timestamp, level, message, context }) => {
              return `${timestamp} [${context || this.context}] ${level}: ${message}`;
            })
          )
        })
      ]
    });

    // Add file transport in production
    if (unifiedConfig.shared.monitoring.logLevel !== 'debug') {
      this.logger.add(new winston.transports.File({
        filename: 'logs/bridge-api.log',
        maxsize: 10 * 1024 * 1024, // 10MB
        maxFiles: 5
      }));
    }
  }

  debug(message: string, meta?: any): void {
    this.logger.debug(message, { context: this.context, ...meta });
  }

  info(message: string, meta?: any): void {
    this.logger.info(message, { context: this.context, ...meta });
  }

  warn(message: string, meta?: any): void {
    this.logger.warn(message, { context: this.context, ...meta });
  }

  error(message: string, error?: Error | any, meta?: any): void {
    this.logger.error(message, { 
      context: this.context, 
      error: error?.stack || error,
      ...meta 
    });
  }
}

// Create default logger instance
export const logger = new Logger('BridgeAPI');