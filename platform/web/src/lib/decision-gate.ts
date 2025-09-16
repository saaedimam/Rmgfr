/**
 * Decision Gate Service (TypeScript)
 * Implements the core decision logic for fraud detection
 */

export enum Action {
  ALLOW = 'allow',
  DENY = 'deny',
  REVIEW = 'review',
  STEP_UP = 'step_up'
}

export interface DecisionMatrix {
  event_type: string;
  risk_band: string;
  customer_segment: string;
  action: Action;
  max_fpr: number;
  notes: string;
}

export interface DecisionContext {
  event_type: string;
  risk_score: number;
  customer_segment: string;
  latest_fpr: number;
}

export interface DecisionResult {
  action: Action;
  confidence: number;
  reasons: string[];
}

export class DecisionGate {
  private decisionMatrix: Map<string, DecisionMatrix> = new Map();

  constructor() {
    this.loadDecisionMatrix();
  }

  private loadDecisionMatrix(): void {
    // Load decision matrix from API or local storage
    console.log('Loading decision matrix...');
    // TODO: Load from API
  }

  private getRiskBand(riskScore: number): string {
    if (riskScore < 0.3) return 'low';
    if (riskScore < 0.6) return 'med';
    if (riskScore < 0.8) return 'high';
    return 'critical';
  }

  private getMatrixKey(eventType: string, riskBand: string, customerSegment: string): string {
    return `${eventType}:${riskBand}:${customerSegment}`;
  }

  /**
   * Core decision function
   * @param context Decision context with event details
   * @param matrixMap Optional decision matrix override
   * @returns Decision result with action, confidence, and reasons
   */
  decide(context: DecisionContext, matrixMap?: Map<string, DecisionMatrix>): DecisionResult {
    try {
      // Get risk band from risk score
      const riskBand = this.getRiskBand(context.risk_score);
      
      // Generate matrix key
      const matrixKey = this.getMatrixKey(
        context.event_type,
        riskBand,
        context.customer_segment
      );
      
      // Use provided matrix or default
      let matrixEntry: DecisionMatrix;
      if (matrixMap && matrixMap.has(matrixKey)) {
        matrixEntry = matrixMap.get(matrixKey)!;
      } else {
        // Fallback to default decision matrix
        matrixEntry = this.getDefaultDecision(context.event_type, riskBand, context.customer_segment);
      }
      
      // Extract action and max FPR
      const action = matrixEntry.action;
      const maxFpr = matrixEntry.max_fpr;
      
      // Check if current FPR exceeds threshold
      if (context.latest_fpr > maxFpr) {
        // FPR too high, escalate to review
        return {
          action: Action.REVIEW,
          confidence: 0.8,
          reasons: [
            `FPR ${context.latest_fpr.toFixed(3)} exceeds threshold ${maxFpr.toFixed(3)}`,
            `Escalating ${action} to review`
          ]
        };
      } else {
        // Normal decision flow
        const confidence = 1.0 - context.risk_score;
        return {
          action,
          confidence,
          reasons: [
            `Risk band: ${riskBand}`,
            `Customer segment: ${context.customer_segment}`,
            `Action: ${action}`,
            `Max FPR: ${maxFpr.toFixed(3)}`
          ]
        };
      }
      
    } catch (error) {
      console.error('Error in decision gate:', error);
      // Fail safe to review
      return {
        action: Action.REVIEW,
        confidence: 0.5,
        reasons: [`Error in decision logic: ${error}`]
      };
    }
  }

  private getDefaultDecision(eventType: string, riskBand: string, customerSegment: string): DecisionMatrix {
    // Default decision matrix based on risk level
    const defaults: Record<string, Partial<DecisionMatrix>> = {
      low: { action: Action.ALLOW, max_fpr: 0.01 },
      med: { action: Action.STEP_UP, max_fpr: 0.008 },
      high: { action: Action.REVIEW, max_fpr: 0.005 },
      critical: { action: Action.DENY, max_fpr: 0.002 }
    };
    
    const defaultEntry = defaults[riskBand] || { action: Action.REVIEW, max_fpr: 0.01 };
    
    return {
      event_type: eventType,
      risk_band: riskBand,
      customer_segment: customerSegment,
      action: defaultEntry.action!,
      max_fpr: defaultEntry.max_fpr!,
      notes: 'Default decision'
    };
  }

  /**
   * Update decision matrix with new data
   */
  updateMatrix(matrixData: DecisionMatrix[]): void {
    console.log(`Updating decision matrix with ${matrixData.length} entries`);
    
    for (const entry of matrixData) {
      const key = this.getMatrixKey(
        entry.event_type,
        entry.risk_band,
        entry.customer_segment
      );
      
      this.decisionMatrix.set(key, entry);
    }
    
    console.log('Decision matrix updated successfully');
  }

  /**
   * Get current decision matrix
   */
  getMatrix(): Map<string, DecisionMatrix> {
    return new Map(this.decisionMatrix);
  }
}

// Export singleton instance
export const decisionGate = new DecisionGate();
