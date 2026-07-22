import type { ActivityItem } from "../types/dashboard";

interface ActivityFeedProps {
  items: ActivityItem[];
}

export function ActivityFeed({ items }: ActivityFeedProps) {
  return (
    <div className="chart-card">
      <h3>Recent Activity</h3>
      {items.length === 0 ? (
        <p className="empty-state">No recent activity.</p>
      ) : (
        <ul className="activity-list">
          {items.map((item) => (
            <li key={`${item.activity_type}-${item.occurred_at}-${item.title}`}>
              <div>
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </div>
              <span>{new Date(item.occurred_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
