import React from 'react';
import { Clock, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';

const HistoryList = ({ history }) => {
    if (!history || history.length === 0) {
        return (
            <div
                className="glass-card text-center"
                style={{ padding: '3rem 2rem' }}
            >
                <Clock size={48} style={{ color: 'var(--neutral-300)', marginBottom: '1rem' }} />
                <p style={{ color: 'var(--text-muted)' }}>No predictions yet. Analyze some text to get started!</p>
            </div>
        );
    }

    const getSentimentIcon = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return <ThumbsUp size={16} />;
            case 'negative':
                return <ThumbsDown size={16} />;
            default:
                return <Minus size={16} />;
        }
    };

    const getSentimentBadgeClass = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return 'badge-positive';
            case 'negative':
                return 'badge-negative';
            default:
                return 'badge-neutral';
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="glass-card" style={{ overflow: 'hidden' }}>
            <div
                className="flex items-center justify-between"
                style={{
                    padding: '1.25rem 1.5rem',
                    borderBottom: '1px solid var(--glass-border)',
                }}
            >
                <div className="flex items-center gap-3">
                    <Clock size={20} style={{ color: 'var(--accent-purple)' }} />
                    <h3 className="heading-3">Recent Predictions</h3>
                </div>
                <span
                    className="badge"
                    style={{
                        background: 'var(--neutral-100)',
                        color: 'var(--neutral-600)',
                    }}
                >
                    {history.length} items
                </span>
            </div>

            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {history.map((item, index) => (
                    <div
                        key={item.id || index}
                        className="animate-slide-in"
                        style={{
                            padding: '1rem 1.5rem',
                            borderBottom: index < history.length - 1 ? '1px solid var(--glass-border)' : 'none',
                            transition: 'background var(--transition-fast)',
                            animationDelay: `${index * 50}ms`,
                            cursor: 'pointer',
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = 'var(--neutral-50)'}
                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                        <div className="flex justify-between items-start" style={{ marginBottom: '0.5rem' }}>
                            <span className={`badge ${getSentimentBadgeClass(item.sentiment)}`}>
                                {getSentimentIcon(item.sentiment)}
                                <span>{item.sentiment}</span>
                            </span>
                            <div className="flex items-center gap-3">
                                <span
                                    style={{
                                        fontSize: '0.875rem',
                                        fontWeight: 600,
                                        color: 'var(--accent-purple)',
                                    }}
                                >
                                    {(item.confidence * 100).toFixed(0)}%
                                </span>
                                <span className="text-small">
                                    {formatTime(item.timestamp)}
                                </span>
                            </div>
                        </div>
                        <p
                            style={{
                                color: 'var(--text-secondary)',
                                fontSize: '0.9375rem',
                                lineHeight: 1.5,
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                            }}
                        >
                            {item.text}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default HistoryList;
