import React from 'react';
import { Activity, TrendingUp, TrendingDown, Zap } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, gradient, iconColor, trend }) => (
    <div className="glass-card stat-card">
        <div
            className="stat-icon"
            style={{
                background: gradient,
            }}
        >
            <Icon size={24} color={iconColor} />
        </div>
        <div>
            <p className="stat-value">{value?.toLocaleString() ?? '-'}</p>
            <p className="stat-label">{title}</p>
            {trend !== undefined && (
                <span
                    style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: trend >= 0 ? 'var(--success-600)' : 'var(--danger-600)',
                    }}
                >
                    {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% today
                </span>
            )}
        </div>
    </div>
);

const StatsDashboard = ({ stats }) => {
    if (!stats) {
        // Skeleton loading
        return (
            <div
                className="grid grid-cols-3 gap-6"
                style={{ marginBottom: '2rem' }}
            >
                {[1, 2, 3].map(i => (
                    <div key={i} className="glass-card" style={{ padding: '1.5rem' }}>
                        <div className="flex items-center gap-4">
                            <div className="skeleton" style={{ width: 56, height: 56, borderRadius: 'var(--radius-xl)' }} />
                            <div>
                                <div className="skeleton" style={{ width: 80, height: 32, marginBottom: 8 }} />
                                <div className="skeleton" style={{ width: 100, height: 16 }} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    const { total_predictions, sentiment_distribution, avg_confidence } = stats;

    // Calculate positive rate
    const positiveRate = total_predictions > 0
        ? ((sentiment_distribution.positive / total_predictions) * 100).toFixed(1)
        : 0;

    return (
        <div
            className="grid gap-6"
            style={{
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                marginBottom: '2rem'
            }}
        >
            <StatCard
                title="Total Analyses"
                value={total_predictions}
                icon={Activity}
                gradient="linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)"
                iconColor="var(--accent-purple)"
            />
            <StatCard
                title="Positive Sentiment"
                value={sentiment_distribution.positive}
                icon={TrendingUp}
                gradient="linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%)"
                iconColor="var(--success-600)"
            />
            <StatCard
                title="Negative Sentiment"
                value={sentiment_distribution.negative}
                icon={TrendingDown}
                gradient="linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(244, 63, 94, 0.2) 100%)"
                iconColor="var(--danger-600)"
            />
            {avg_confidence !== undefined && (
                <StatCard
                    title="Avg Confidence"
                    value={`${(avg_confidence * 100).toFixed(1)}%`}
                    icon={Zap}
                    gradient="linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(251, 191, 36, 0.2) 100%)"
                    iconColor="var(--warning-600)"
                />
            )}
        </div>
    );
};

export default StatsDashboard;
