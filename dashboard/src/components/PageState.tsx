interface PageStateProps {
  loading?: boolean;
  error?: string | null;
  empty?: string | null;
}

export function PageState({ loading, error, empty }: PageStateProps) {
  if (loading) {
    return <p className="page-state">Loading...</p>;
  }
  if (error) {
    return <p className="page-state error">{error}</p>;
  }
  if (empty) {
    return <p className="empty-state">{empty}</p>;
  }
  return null;
}
