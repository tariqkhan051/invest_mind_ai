import type { Recommendation } from "../types/dashboard";
import { buildRecommendationAction } from "../utils/recommendationAction";

interface RecommendationCardProps {
  recommendation: Recommendation;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const action = buildRecommendationAction(recommendation);

  return (
    <article className="recommendation-card">
      <div className="recommendation-header">
        <span className="pill">{recommendation.recommendation_type}</span>
        <span className="confidence">
          {Number(recommendation.confidence).toFixed(0)}% confidence
        </span>
      </div>
      <h4 className="action-headline">{action.headline}</h4>
      {action.routeLabel ? (
        <p className="action-route">{action.routeLabel}</p>
      ) : null}
      {action.amountLabel ? (
        <p className="action-amount">{action.amountLabel}</p>
      ) : null}
      <p>{action.detail}</p>
      {action.meta.length > 0 ? (
        <p className="action-meta">{action.meta.join(" · ")}</p>
      ) : null}
    </article>
  );
}
