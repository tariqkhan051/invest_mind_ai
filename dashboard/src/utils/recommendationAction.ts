import type { Recommendation } from "../types/dashboard";
import { formatCurrency, formatPercent } from "./format";

export interface RecommendationActionView {
  headline: string;
  amountLabel: string | null;
  routeLabel: string | null;
  detail: string;
  meta: string[];
}

export function buildRecommendationAction(
  recommendation: Recommendation,
): RecommendationActionView {
  const amount = recommendation.recommended_amount
    ? formatCurrency(recommendation.recommended_amount)
    : null;
  const fromSymbol =
    recommendation.from_symbol ??
    recommendation.supporting_evidence?.from_symbol ??
    null;
  const toSymbol =
    recommendation.to_symbol ??
    recommendation.supporting_evidence?.to_symbol ??
    null;
  const symbol =
    recommendation.symbol ??
    recommendation.supporting_evidence?.symbol ??
    null;
  const type = recommendation.recommendation_type;

  let headline = "Review portfolio action";
  let routeLabel: string | null = null;
  let amountLabel: string | null = amount ? `Amount ${amount}` : null;

  if (type === "switch" && fromSymbol && toSymbol) {
    headline = amount
      ? `Move ${amount} from ${fromSymbol} → ${toSymbol}`
      : `Switch from ${fromSymbol} → ${toSymbol}`;
    routeLabel = `${fromSymbol} → ${toSymbol}`;
    amountLabel = amount ? `Switch amount ${amount}` : null;
  } else if (type === "invest" && symbol) {
    headline = amount
      ? `Invest ${amount} into ${symbol}`
      : `Invest into ${symbol}`;
    routeLabel = `Cash → ${symbol}`;
  } else if (type === "buy" && symbol) {
    headline = amount ? `Buy ${amount} of ${symbol}` : `Buy ${symbol}`;
    routeLabel = `Cash → ${symbol}`;
  } else if (type === "sell" && symbol) {
    headline = amount ? `Sell ${amount} of ${symbol}` : `Sell ${symbol}`;
    routeLabel = `${symbol} → Cash`;
  } else if (type === "hold_cash") {
    headline = amount ? `Hold ${amount} as cash` : "Hold cash / wait";
    routeLabel = "Keep cash uninvested";
  } else if (type === "continue_sip") {
    headline = amount ? `Continue SIP of ${amount}` : "Continue monthly SIP";
  } else if (type === "redeem" && symbol) {
    headline = amount ? `Redeem ${amount} from ${symbol}` : `Redeem ${symbol}`;
  } else if (type === "wait" || type === "no_action") {
    headline = "No action today";
    amountLabel = null;
  }

  const meta: string[] = [];
  if (recommendation.expected_return) {
    meta.push(`Expected ${formatPercent(recommendation.expected_return)}`);
  }
  if (recommendation.expected_risk) {
    meta.push(`Risk: ${recommendation.expected_risk}`);
  }
  if (recommendation.supporting_evidence?.as_of_date) {
    meta.push(`As of ${recommendation.supporting_evidence.as_of_date}`);
  }

  return {
    headline,
    amountLabel,
    routeLabel,
    detail: recommendation.reason,
    meta,
  };
}
