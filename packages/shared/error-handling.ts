/**
 * Unified error handling system
 * Bridges error responses across web, mobile, and API
 */

export enum ErrorCode {
  // Authentication errors
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  
  // Validation errors
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_INPUT = 'INVALID_INPUT',
  MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD',
  
  // Business logic errors
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS',
  RESOURCE_NOT_FOUND = 'RESOURCE_NOT_FOUND',
  RESOURCE_ALREADY_EXISTS = 'RESOURCE_ALREADY_EXISTS',
  
  // System errors
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  TIMEOUT = 'TIMEOUT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  
  // Fraud detection errors
  FRAUD_DETECTED = 'FRAUD_DETECTED',
  HIGH_RISK_TRANSACTION = 'HIGH_RISK_TRANSACTION',
  SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY',
}

export interface ErrorDetails {
  code: ErrorCode;
  message: string;
  field?: string;
  value?: any;
  timestamp: string;
  requestId?: string;
  context?: Record<string, any>;
}

export interface ApiError extends Error {
  code: ErrorCode;
  statusCode: number;
  details: ErrorDetails;
  isRetryable: boolean;
}

export class FraudDetectionError extends Error implements ApiError {
  public readonly code: ErrorCode;
  public readonly statusCode: number;
  public readonly details: ErrorDetails;
  public readonly isRetryable: boolean;

  constructor(
    code: ErrorCode,
    message: string,
    statusCode: number = 400,
    isRetryable: boolean = false,
    context?: Record<string, any>
  ) {
    super(message);
    this.name = 'FraudDetectionError';
    this.code = code;
    this.statusCode = statusCode;
    this.isRetryable = isRetryable;
    this.details = {
      code,
      message,
      timestamp: new Date().toISOString(),
      context,
    };
  }
}

export class ValidationError extends FraudDetectionError {
  constructor(
    message: string,
    field?: string,
    value?: any,
    context?: Record<string, any>
  ) {
    super(
      ErrorCode.VALIDATION_ERROR,
      message,
      400,
      false,
      { field, value, ...context }
    );
    this.name = 'ValidationError';
    this.details.field = field;
    this.details.value = value;
  }
}

export class RateLimitError extends FraudDetectionError {
  constructor(
    message: string = 'Rate limit exceeded',
    retryAfter?: number,
    context?: Record<string, any>
  ) {
    super(
      ErrorCode.RATE_LIMIT_EXCEEDED,
      message,
      429,
      true,
      { retryAfter, ...context }
    );
    this.name = 'RateLimitError';
  }
}

export class FraudDetectedError extends FraudDetectionError {
  constructor(
    message: string = 'Fraud detected',
    riskScore?: number,
    reasons?: string[],
    context?: Record<string, any>
  ) {
    super(
      ErrorCode.FRAUD_DETECTED,
      message,
      403,
      false,
      { riskScore, reasons, ...context }
    );
    this.name = 'FraudDetectedError';
  }
}

/**
 * Error handler for API responses
 */
export class ApiErrorHandler {
  static fromResponse(response: Response, body?: any): ApiError {
    const statusCode = response.status;
    const errorCode = this.getErrorCodeFromStatus(statusCode);
    
    const message = body?.message || body?.detail || response.statusText || 'Unknown error';
    const isRetryable = this.isRetryableStatus(statusCode);
    
    return new FraudDetectionError(
      errorCode,
      message,
      statusCode,
      isRetryable,
      {
        url: response.url,
        method: response.headers.get('x-request-method'),
        requestId: response.headers.get('x-request-id'),
        ...body
      }
    );
  }

  static fromNetworkError(error: Error): ApiError {
    return new FraudDetectionError(
      ErrorCode.NETWORK_ERROR,
      error.message,
      0,
      true,
      { originalError: error.name }
    );
  }

  static fromTimeout(): ApiError {
    return new FraudDetectionError(
      ErrorCode.TIMEOUT,
      'Request timeout',
      408,
      true
    );
  }

  private static getErrorCodeFromStatus(statusCode: number): ErrorCode {
    switch (statusCode) {
      case 400:
        return ErrorCode.VALIDATION_ERROR;
      case 401:
        return ErrorCode.UNAUTHORIZED;
      case 403:
        return ErrorCode.FORBIDDEN;
      case 404:
        return ErrorCode.RESOURCE_NOT_FOUND;
      case 409:
        return ErrorCode.RESOURCE_ALREADY_EXISTS;
      case 429:
        return ErrorCode.RATE_LIMIT_EXCEEDED;
      case 500:
        return ErrorCode.INTERNAL_ERROR;
      case 503:
        return ErrorCode.SERVICE_UNAVAILABLE;
      default:
        return ErrorCode.INTERNAL_ERROR;
    }
  }

  private static isRetryableStatus(statusCode: number): boolean {
    return statusCode >= 500 || statusCode === 429 || statusCode === 408;
  }
}

/**
 * Error formatter for user-facing messages
 */
export class ErrorFormatter {
  static formatForUser(error: ApiError): string {
    switch (error.code) {
      case ErrorCode.UNAUTHORIZED:
        return 'Please log in to continue';
      case ErrorCode.FORBIDDEN:
        return 'You do not have permission to perform this action';
      case ErrorCode.VALIDATION_ERROR:
        return error.details.field 
          ? `Invalid ${error.details.field}: ${error.message}`
          : error.message;
      case ErrorCode.RATE_LIMIT_EXCEEDED:
        return 'Too many requests. Please try again later';
      case ErrorCode.FRAUD_DETECTED:
        return 'Transaction blocked due to security concerns';
      case ErrorCode.HIGH_RISK_TRANSACTION:
        return 'Transaction requires additional verification';
      case ErrorCode.NETWORK_ERROR:
        return 'Network error. Please check your connection';
      case ErrorCode.TIMEOUT:
        return 'Request timed out. Please try again';
      default:
        return 'An unexpected error occurred. Please try again';
    }
  }

  static formatForLogging(error: ApiError): string {
    return JSON.stringify({
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      isRetryable: error.isRetryable,
      details: error.details,
      stack: error.stack,
    });
  }
}

/**
 * Retry logic for retryable errors
 */
export class RetryHandler {
  static async withRetry<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        // Don't retry if it's not a retryable error
        if (error instanceof FraudDetectionError && !error.isRetryable) {
          throw error;
        }
        
        // Don't retry on last attempt
        if (attempt === maxRetries) {
          break;
        }
        
        // Calculate delay with exponential backoff
        const delay = baseDelay * Math.pow(2, attempt);
        await this.delay(delay);
      }
    }
    
    throw lastError!;
  }

  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Error boundary for React components
 */
export class ErrorBoundary {
  static create(errorHandler: (error: Error) => void) {
    return class extends Error {
      constructor(error: Error) {
        super(error.message);
        this.name = 'ErrorBoundary';
        errorHandler(error);
      }
    };
  }
}

/**
 * Global error handler
 */
export class GlobalErrorHandler {
  private static handlers: Array<(error: ApiError) => void> = [];

  static addHandler(handler: (error: ApiError) => void): void {
    this.handlers.push(handler);
  }

  static removeHandler(handler: (error: ApiError) => void): void {
    const index = this.handlers.indexOf(handler);
    if (index > -1) {
      this.handlers.splice(index, 1);
    }
  }

  static handle(error: ApiError): void {
    this.handlers.forEach(handler => {
      try {
        handler(error);
      } catch (handlerError) {
        console.error('Error handler failed:', handlerError);
      }
    });
  }
}

// Export error types for easy importing
export {
  FraudDetectionError as ApiError,
  ValidationError,
  RateLimitError,
  FraudDetectedError,
};
