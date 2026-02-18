
import { PilotAction, MoralMetrics } from '../../types';

export class MoralCalculator {
  private threshold: number;

  constructor(threshold: number = 0.5) {
    this.threshold = threshold;
  }

  /**
   * Calculates the moral vector magnitude for a given action.
   *
   * Formula:
   * magnitude = sqrt(harm^2 + (1 - utility)^2 + uncertainty^2)
   * scaled_magnitude = magnitude * scale * log(agents_affected + 1)
   *
   * If action is irreversible, scaled_magnitude is doubled.
   */
  public calculateMoralVector(action: PilotAction): number {
    const { harm, utility, uncertainty, agents_affected } = action.metrics;

    // Geometric magnitude calculation
    const magnitude = Math.sqrt(
      Math.pow(harm, 2) +
      Math.pow(1 - utility, 2) +
      Math.pow(uncertainty, 2)
    );

    // Apply scaling factors
    // Using Math.log() which is natural log (ln), consistent with Python's math.log()
    let scaledMagnitude = magnitude * action.scale * Math.log(agents_affected + 1);

    // Apply entropy penalty
    if (action.entropy_class === 'IRREVERSIBLE') {
      scaledMagnitude *= 2;
    }

    return scaledMagnitude;
  }

  public evaluateAction(action: PilotAction): { approved: boolean; reason: string; score: number } {
    const score = this.calculateMoralVector(action);
    const approved = score < this.threshold;

    return {
      approved,
      reason: approved
        ? `Moral vector (${score.toFixed(3)}) within safety threshold (< ${this.threshold})`
        : `Moral vector (${score.toFixed(3)}) exceeds safety threshold (> ${this.threshold})`,
      score
    };
  }
}

export const defaultMoralKernel = new MoralCalculator(1.5); // Slightly higher threshold for demo purposes
