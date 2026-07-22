import type { Recommendation } from "../types/dashboard";

interface RecommendationCardProps {
  recommendation: Recommendation;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <article className="recommendation-card">
      <div className="recommendation-header">
        <span className="pill">{recommendation.recommendation_type}</span>
        <span className="confidence">{recommendation.confidence}% confidence</span>
      </div>
      <h4>{recommendation.symbol ?? "Portfolio action"}</h4>
      <p>{recommendation.reason}</p>
    </article>
  );
}
