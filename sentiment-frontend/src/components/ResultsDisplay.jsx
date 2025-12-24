import React from 'react';
import { ThumbsUp, ThumbsDown, Minus, Zap, Clock, Cpu } from 'lucide-react';

const ResultsDisplay = ({ result }) => {
    if (!result) return null;

    const getSentimentConfig = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return {
                    icon: ThumbsUp,
                    gradient: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                    bgColor: 'var(--success-50)',
                    borderColor: 'var(--success-200)',
                    textColor: 'var(--success-700)',
                    label: 'Positive Sentiment',
                };
            case 'negative':
                return {
                    icon: ThumbsDown,
                    gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    bgColor: 'var(--danger-50)',
                    borderColor: 'var(--danger-200)',
                    textColor: 'var(--danger-700)',
                    label: 'Negative Sentiment',
                };
            default:
                return {
                    icon: Minus,
                    gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
                    bgColor: 'var(--neutral-100)',
                    borderColor: 'var(--neutral-300)',
                    textColor: 'var(--neutral-700)',
                    label: 'Neutral Sentiment',
                };
        }
    };

    const config = getSentimentConfig(result.sentiment);
    const Icon = config.icon;

    return (
        <div
            className="glass-card animate-fade-in"
            style={{
                padding: '2rem',
                marginBottom: '2rem',
                background: config.bgColor,
                border: `2px solid ${config.borderColor}`,
            }}
        >
            {/* Header */}
            <div className="flex items-center justify-between" style={{ marginBottom: '1.5rem' }}>
                <div className="flex items-center gap-4">
                    <div
                        style={{
                            width: 60,
                            height: 60,
                            borderRadius: 'var(--radius-xl)',
                            background: config.gradient,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: '0 4px 14px rgba(0,0,0,0.15)',
                        }}
                    >
                        <Icon size={28} color="white" />
                    </div>
                    <div>
                        <h3
                            style={{
                                fontSize: '1.5rem',
                                fontWeight: 700,
                                color: config.textColor,
                                textTransform: 'capitalize',
                            }}
                        >
                            {config.label}
                        </h3>
                        <div className="flex items-center gap-2" style={{ marginTop: '0.25rem' }}>
                            <Zap size={14} style={{ color: 'var(--warning-500)' }} />
                            <span className="text-small">
                                Confidence: {(result.confidence * 100).toFixed(1)}%
                            </span>
                        </div>
                    </div>
                </div>

                {/* Confidence Gauge */}
                <div style={{ textAlign: 'center' }}>
                    <div
                        style={{
                            width: 80,
                            height: 80,
                            borderRadius: '50%',
                            background: `conic-gradient(${config.gradient.match(/#[a-f0-9]+/gi)[0]} ${result.confidence * 360}deg, var(--neutral-200) 0deg)`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            position: 'relative',
                        }}
                    >
                        <div
                            style={{
                                width: 60,
                                height: 60,
                                borderRadius: '50%',
                                background: 'white',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 700,
                                fontSize: '1rem',
                                color: config.textColor,
                            }}
                        >
                            {(result.confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Score Bars */}
            <div style={{ display: 'grid', gap: '1rem' }}>
                {/* Positive Score */}
                <div>
                    <div className="flex justify-between" style={{ marginBottom: '0.5rem' }}>
                        <span className="text-small" style={{ fontWeight: 500 }}>Positive Score</span>
                        <span style={{ fontWeight: 600, color: 'var(--success-600)' }}>
                            {(result.positive_score * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill progress-positive"
                            style={{ width: `${result.positive_score * 100}%` }}
                        />
                    </div>
                </div>

                {/* Negative Score */}
                <div>
                    <div className="flex justify-between" style={{ marginBottom: '0.5rem' }}>
                        <span className="text-small" style={{ fontWeight: 500 }}>Negative Score</span>
                        <span style={{ fontWeight: 600, color: 'var(--danger-600)' }}>
                            {(result.negative_score * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill progress-negative"
                            style={{ width: `${result.negative_score * 100}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Metadata */}
            <div
                className="flex gap-6"
                style={{
                    marginTop: '1.5rem',
                    paddingTop: '1rem',
                    borderTop: '1px solid var(--neutral-200)',
                }}
            >
                {result.processing_time_ms && (
                    <div className="flex items-center gap-2">
                        <Cpu size={14} style={{ color: 'var(--neutral-400)' }} />
                        <span className="text-small">
                            {result.processing_time_ms.toFixed(1)}ms processing
                        </span>
                    </div>
                )}
                {result.model_version && (
                    <div className="flex items-center gap-2">
                        <span className="text-small">Model: {result.model_version}</span>
                    </div>
                )}
                {result.timestamp && (
                    <div className="flex items-center gap-2">
                        <Clock size={14} style={{ color: 'var(--neutral-400)' }} />
                        <span className="text-small">
                            {new Date(result.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultsDisplay;
