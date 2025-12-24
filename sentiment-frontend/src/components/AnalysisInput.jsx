import React, { useState } from 'react';
import { Send, Sparkles, Lightbulb } from 'lucide-react';

const EXAMPLE_TEXTS = [
    "This product exceeded all my expectations! The quality is outstanding.",
    "Terrible experience, would not recommend to anyone.",
    "It's okay, nothing special but does the job.",
    "Absolutely love it! Best purchase I've made this year.",
    "Very disappointed with the customer service.",
];

const AnalysisInput = ({ onAnalyze, loading }) => {
    const [text, setText] = useState("");
    const [charCount, setCharCount] = useState(0);

    const handleTextChange = (e) => {
        const value = e.target.value;
        setText(value);
        setCharCount(value.length);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (text.trim()) {
            onAnalyze(text);
            setText("");
            setCharCount(0);
        }
    };

    const handleExample = () => {
        const example = EXAMPLE_TEXTS[Math.floor(Math.random() * EXAMPLE_TEXTS.length)];
        setText(example);
        setCharCount(example.length);
    };

    return (
        <div
            className="glass-card animate-fade-in"
            style={{ padding: '2rem', marginBottom: '2rem' }}
        >
            <div className="flex items-center justify-between" style={{ marginBottom: '1.5rem' }}>
                <div className="flex items-center gap-3">
                    <div
                        style={{
                            width: 40,
                            height: 40,
                            borderRadius: 'var(--radius-lg)',
                            background: 'var(--accent-gradient)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <Sparkles size={20} color="white" />
                    </div>
                    <div>
                        <h2 className="heading-3">Analyze Sentiment</h2>
                        <p className="text-small">Enter text to analyze its emotional tone</p>
                    </div>
                </div>
                <button
                    type="button"
                    onClick={handleExample}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.8125rem' }}
                >
                    <Lightbulb size={16} />
                    Try Example
                </button>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="input-wrapper" style={{ marginBottom: '1rem' }}>
                    <textarea
                        className="input textarea"
                        placeholder="Enter customer review, feedback, or any text to analyze..."
                        value={text}
                        onChange={handleTextChange}
                        disabled={loading}
                        maxLength={5000}
                        style={{
                            minHeight: '140px',
                            resize: 'vertical',
                        }}
                    />
                    <div
                        className="flex justify-between items-center"
                        style={{
                            marginTop: '0.5rem',
                            padding: '0 0.25rem',
                        }}
                    >
                        <span className="text-small">
                            {charCount > 0 && `${charCount} / 5000 characters`}
                        </span>
                        <span className="text-small">
                            {text.trim().split(/\s+/).filter(Boolean).length} words
                        </span>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={!text.trim() || loading}
                    className="btn btn-primary btn-lg"
                    style={{ width: '100%' }}
                >
                    {loading ? (
                        <>
                            <div
                                className="animate-spin"
                                style={{
                                    width: 20,
                                    height: 20,
                                    border: '2px solid rgba(255,255,255,0.3)',
                                    borderTopColor: 'white',
                                    borderRadius: '50%',
                                }}
                            />
                            <span>Analyzing Sentiment...</span>
                        </>
                    ) : (
                        <>
                            <Send size={18} />
                            <span>Analyze Sentiment</span>
                        </>
                    )}
                </button>
            </form>
        </div>
    );
};

export default AnalysisInput;
