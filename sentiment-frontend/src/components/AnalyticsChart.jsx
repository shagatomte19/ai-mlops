import React from 'react';
import { TrendingUp, TrendingDown, BarChart3, PieChart } from 'lucide-react';

const AnalyticsChart = ({ analytics }) => {
    if (!analytics) {
        return (
            <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
                <BarChart3 size={48} style={{ color: 'var(--neutral-300)', marginBottom: '1rem' }} />
                <p style={{ color: 'var(--text-muted)' }}>Loading analytics data...</p>
            </div>
        );
    }

    const { trend_data, sentiment_distribution, confidence_distribution, top_words } = analytics;

    // Calculate max for scaling
    const maxTrendValue = Math.max(...trend_data.map(d => d.positive + d.negative + (d.neutral || 0)), 1);

    // Format distribution for pie chart visual
    const total = sentiment_distribution.positive + sentiment_distribution.negative + (sentiment_distribution.neutral || 0);
    const positivePercent = total > 0 ? (sentiment_distribution.positive / total * 100).toFixed(1) : 0;
    const negativePercent = total > 0 ? (sentiment_distribution.negative / total * 100).toFixed(1) : 0;
    const neutralPercent = total > 0 ? ((sentiment_distribution.neutral || 0) / total * 100).toFixed(1) : 0;

    return (
        <div style={{ display: 'grid', gap: '1.5rem' }}>
            {/* Trend Chart */}
            <div className="glass-card" style={{ padding: '1.5rem' }}>
                <div className="flex items-center gap-3" style={{ marginBottom: '1.5rem' }}>
                    <TrendingUp size={20} style={{ color: 'var(--accent-purple)' }} />
                    <h3 className="heading-3">Sentiment Trends (Last 7 Days)</h3>
                </div>

                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '200px' }}>
                    {trend_data.map((day, index) => {
                        const dayTotal = day.positive + day.negative + (day.neutral || 0);
                        const barHeight = maxTrendValue > 0 ? (dayTotal / maxTrendValue) * 180 : 0;
                        const positiveHeight = dayTotal > 0 ? (day.positive / dayTotal) * barHeight : 0;
                        const negativeHeight = dayTotal > 0 ? (day.negative / dayTotal) * barHeight : 0;
                        const neutralHeight = barHeight - positiveHeight - negativeHeight;

                        return (
                            <div
                                key={index}
                                style={{
                                    flex: 1,
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    gap: '8px',
                                }}
                            >
                                <div
                                    style={{
                                        width: '100%',
                                        height: `${barHeight}px`,
                                        minHeight: '4px',
                                        borderRadius: 'var(--radius-md)',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        flexDirection: 'column-reverse',
                                        transition: 'height 0.5s ease-out',
                                    }}
                                >
                                    <div
                                        style={{
                                            height: `${positiveHeight}px`,
                                            background: 'linear-gradient(180deg, #22c55e 0%, #16a34a 100%)',
                                        }}
                                        title={`Positive: ${day.positive}`}
                                    />
                                    {neutralHeight > 0 && (
                                        <div
                                            style={{
                                                height: `${neutralHeight}px`,
                                                background: 'linear-gradient(180deg, #94a3b8 0%, #64748b 100%)',
                                            }}
                                            title={`Neutral: ${day.neutral || 0}`}
                                        />
                                    )}
                                    <div
                                        style={{
                                            height: `${negativeHeight}px`,
                                            background: 'linear-gradient(180deg, #ef4444 0%, #dc2626 100%)',
                                        }}
                                        title={`Negative: ${day.negative}`}
                                    />
                                </div>
                                <span className="text-small" style={{ fontSize: '0.6875rem' }}>
                                    {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                                </span>
                            </div>
                        );
                    })}
                </div>

                {/* Legend */}
                <div className="flex justify-center gap-6" style={{ marginTop: '1rem' }}>
                    <div className="flex items-center gap-2">
                        <div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--success-500)' }} />
                        <span className="text-small">Positive</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--danger-500)' }} />
                        <span className="text-small">Negative</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--neutral-400)' }} />
                        <span className="text-small">Neutral</span>
                    </div>
                </div>
            </div>

            {/* Distribution & Words Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                {/* Sentiment Distribution */}
                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <div className="flex items-center gap-3" style={{ marginBottom: '1.5rem' }}>
                        <PieChart size={20} style={{ color: 'var(--accent-purple)' }} />
                        <h3 className="heading-3">Sentiment Distribution</h3>
                    </div>

                    <div className="flex items-center justify-center" style={{ marginBottom: '1.5rem' }}>
                        <div
                            style={{
                                width: 150,
                                height: 150,
                                borderRadius: '50%',
                                background: `conic-gradient(
                  var(--success-500) 0deg ${positivePercent * 3.6}deg,
                  var(--danger-500) ${positivePercent * 3.6}deg ${(parseFloat(positivePercent) + parseFloat(negativePercent)) * 3.6}deg,
                  var(--neutral-400) ${(parseFloat(positivePercent) + parseFloat(negativePercent)) * 3.6}deg 360deg
                )`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <div
                                style={{
                                    width: 100,
                                    height: 100,
                                    borderRadius: '50%',
                                    background: 'var(--glass-bg)',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}
                            >
                                <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{total}</span>
                                <span className="text-small">Total</span>
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gap: '0.75rem' }}>
                        <div className="flex justify-between">
                            <span className="flex items-center gap-2">
                                <div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--success-500)' }} />
                                Positive
                            </span>
                            <span style={{ fontWeight: 600 }}>{sentiment_distribution.positive} ({positivePercent}%)</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="flex items-center gap-2">
                                <div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--danger-500)' }} />
                                Negative
                            </span>
                            <span style={{ fontWeight: 600 }}>{sentiment_distribution.negative} ({negativePercent}%)</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="flex items-center gap-2">
                                <div style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--neutral-400)' }} />
                                Neutral
                            </span>
                            <span style={{ fontWeight: 600 }}>{sentiment_distribution.neutral || 0} ({neutralPercent}%)</span>
                        </div>
                    </div>
                </div>

                {/* Top Words */}
                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <div className="flex items-center gap-3" style={{ marginBottom: '1.5rem' }}>
                        <BarChart3 size={20} style={{ color: 'var(--accent-purple)' }} />
                        <h3 className="heading-3">Top Words</h3>
                    </div>

                    {top_words && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            {/* Positive Words */}
                            <div>
                                <h4 style={{
                                    fontSize: '0.75rem',
                                    fontWeight: 600,
                                    color: 'var(--success-600)',
                                    marginBottom: '0.5rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em',
                                }}>
                                    Positive Context
                                </h4>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                    {Object.entries(top_words.positive || {}).slice(0, 8).map(([word, count]) => (
                                        <span
                                            key={word}
                                            style={{
                                                padding: '2px 8px',
                                                fontSize: '0.75rem',
                                                borderRadius: 'var(--radius-full)',
                                                background: 'var(--success-100)',
                                                color: 'var(--success-700)',
                                            }}
                                        >
                                            {word}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Negative Words */}
                            <div>
                                <h4 style={{
                                    fontSize: '0.75rem',
                                    fontWeight: 600,
                                    color: 'var(--danger-600)',
                                    marginBottom: '0.5rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em',
                                }}>
                                    Negative Context
                                </h4>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                    {Object.entries(top_words.negative || {}).slice(0, 8).map(([word, count]) => (
                                        <span
                                            key={word}
                                            style={{
                                                padding: '2px 8px',
                                                fontSize: '0.75rem',
                                                borderRadius: 'var(--radius-full)',
                                                background: 'var(--danger-100)',
                                                color: 'var(--danger-700)',
                                            }}
                                        >
                                            {word}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Confidence Distribution */}
            {confidence_distribution && confidence_distribution.length > 0 && (
                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    <div className="flex items-center gap-3" style={{ marginBottom: '1.5rem' }}>
                        <BarChart3 size={20} style={{ color: 'var(--accent-purple)' }} />
                        <h3 className="heading-3">Confidence Distribution</h3>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '4px', height: '120px' }}>
                        {confidence_distribution.map((bucket, index) => {
                            const maxCount = Math.max(...confidence_distribution.map(b => b.count), 1);
                            const height = (bucket.count / maxCount) * 100;

                            return (
                                <div
                                    key={index}
                                    style={{
                                        flex: 1,
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '4px',
                                    }}
                                >
                                    <div
                                        style={{
                                            width: '100%',
                                            height: `${height}px`,
                                            minHeight: bucket.count > 0 ? '4px' : '0',
                                            background: 'var(--accent-gradient)',
                                            borderRadius: 'var(--radius-sm)',
                                            transition: 'height 0.5s ease-out',
                                        }}
                                        title={`${bucket.range}: ${bucket.count} predictions`}
                                    />
                                    <span
                                        className="text-small"
                                        style={{
                                            fontSize: '0.625rem',
                                            whiteSpace: 'nowrap',
                                        }}
                                    >
                                        {bucket.range}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyticsChart;
