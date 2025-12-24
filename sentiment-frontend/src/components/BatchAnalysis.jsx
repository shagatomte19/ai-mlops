import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Download, CheckCircle } from 'lucide-react';

const BatchAnalysis = ({ onAnalyze, loading }) => {
    const [texts, setTexts] = useState('');
    const [results, setResults] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;

            if (file.name.endsWith('.csv')) {
                // Parse CSV - assume first column is text
                const lines = content.split('\n').slice(1); // Skip header
                const texts = lines
                    .map(line => {
                        const match = line.match(/^"?([^",]+)"?/);
                        return match ? match[1].trim() : line.split(',')[0]?.trim();
                    })
                    .filter(Boolean);
                setTexts(texts.join('\n'));
            } else {
                // Plain text - one per line
                setTexts(content);
            }
        };
        reader.readAsText(file);
    };

    const handleSubmit = async () => {
        const textList = texts
            .split('\n')
            .map(t => t.trim())
            .filter(Boolean);

        if (textList.length === 0) return;

        try {
            const result = await onAnalyze(textList);
            setResults(result);
        } catch (error) {
            console.error('Batch analysis failed:', error);
        }
    };

    const handleClear = () => {
        setTexts('');
        setResults(null);
    };

    const exportResults = () => {
        if (!results) return;

        const csv = [
            'text,sentiment,confidence,positive_score,negative_score',
            ...results.results.map(r =>
                `"${r.text || ''}",${r.sentiment},${r.confidence},${r.positive_score},${r.negative_score}`
            )
        ].join('\n');

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'batch_results.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    };

    const textCount = texts.split('\n').filter(t => t.trim()).length;

    return (
        <div className="glass-card" style={{ padding: '2rem' }}>
            <div className="flex items-center gap-3" style={{ marginBottom: '1.5rem' }}>
                <div
                    style={{
                        width: 40,
                        height: 40,
                        borderRadius: 'var(--radius-lg)',
                        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <FileText size={20} color="white" />
                </div>
                <div>
                    <h2 className="heading-3">Batch Analysis</h2>
                    <p className="text-small">Analyze multiple texts at once (max 100)</p>
                </div>
            </div>

            {!results ? (
                <>
                    {/* File Drop Zone */}
                    <div
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        style={{
                            border: `2px dashed ${dragActive ? 'var(--accent-purple)' : 'var(--neutral-300)'}`,
                            borderRadius: 'var(--radius-xl)',
                            padding: '2rem',
                            textAlign: 'center',
                            marginBottom: '1rem',
                            cursor: 'pointer',
                            transition: 'all var(--transition-normal)',
                            background: dragActive ? 'rgba(139, 92, 246, 0.05)' : 'transparent',
                        }}
                    >
                        <Upload
                            size={32}
                            style={{
                                color: dragActive ? 'var(--accent-purple)' : 'var(--neutral-400)',
                                marginBottom: '0.5rem',
                            }}
                        />
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                            Drop a CSV or TXT file here, or click to browse
                        </p>
                        <p className="text-small">
                            Supports .csv and .txt files
                        </p>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".csv,.txt"
                            style={{ display: 'none' }}
                            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                        />
                    </div>

                    {/* Divider */}
                    <div
                        className="flex items-center"
                        style={{ margin: '1.5rem 0', gap: '1rem' }}
                    >
                        <div style={{ flex: 1, height: 1, background: 'var(--neutral-200)' }} />
                        <span className="text-small">OR</span>
                        <div style={{ flex: 1, height: 1, background: 'var(--neutral-200)' }} />
                    </div>

                    {/* Text Input */}
                    <textarea
                        className="input textarea"
                        placeholder="Enter texts to analyze, one per line...

Example:
I love this product!
This was a terrible experience.
It's okay, nothing special."
                        value={texts}
                        onChange={(e) => setTexts(e.target.value)}
                        style={{ minHeight: '200px', marginBottom: '1rem' }}
                    />

                    <div className="flex justify-between items-center">
                        <span className="text-small">
                            {textCount} text{textCount !== 1 ? 's' : ''} ready to analyze
                        </span>
                        <div className="flex gap-2">
                            <button
                                className="btn btn-secondary"
                                onClick={handleClear}
                                disabled={!texts}
                            >
                                <X size={16} />
                                Clear
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleSubmit}
                                disabled={textCount === 0 || loading || textCount > 100}
                            >
                                {loading ? (
                                    <>
                                        <div
                                            className="animate-spin"
                                            style={{
                                                width: 16,
                                                height: 16,
                                                border: '2px solid rgba(255,255,255,0.3)',
                                                borderTopColor: 'white',
                                                borderRadius: '50%',
                                            }}
                                        />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>Analyze {textCount} Text{textCount !== 1 ? 's' : ''}</>
                                )}
                            </button>
                        </div>
                    </div>
                </>
            ) : (
                /* Results View */
                <div>
                    <div
                        className="flex items-center justify-between"
                        style={{ marginBottom: '1.5rem' }}
                    >
                        <div className="flex items-center gap-2">
                            <CheckCircle size={24} style={{ color: 'var(--success-500)' }} />
                            <span style={{ fontWeight: 600, color: 'var(--success-700)' }}>
                                Analysis Complete!
                            </span>
                        </div>
                        <div className="flex gap-2">
                            <button className="btn btn-secondary" onClick={exportResults}>
                                <Download size={16} />
                                Export CSV
                            </button>
                            <button className="btn btn-primary" onClick={handleClear}>
                                New Batch
                            </button>
                        </div>
                    </div>

                    {/* Summary */}
                    <div
                        className="grid gap-4"
                        style={{
                            gridTemplateColumns: 'repeat(3, 1fr)',
                            marginBottom: '1.5rem',
                        }}
                    >
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                                {results.total_processed}
                            </div>
                            <div className="text-small">Total Processed</div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--success-600)' }}>
                                {results.results.filter(r => r.sentiment === 'positive').length}
                            </div>
                            <div className="text-small">Positive</div>
                        </div>
                        <div style={{ textAlign: 'center', padding: '1rem' }}>
                            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--danger-600)' }}>
                                {results.results.filter(r => r.sentiment === 'negative').length}
                            </div>
                            <div className="text-small">Negative</div>
                        </div>
                    </div>

                    {/* Results List */}
                    <div
                        style={{
                            maxHeight: '300px',
                            overflowY: 'auto',
                            border: '1px solid var(--neutral-200)',
                            borderRadius: 'var(--radius-lg)',
                        }}
                    >
                        {results.results.map((result, index) => (
                            <div
                                key={index}
                                style={{
                                    padding: '0.75rem 1rem',
                                    borderBottom: index < results.results.length - 1 ? '1px solid var(--neutral-100)' : 'none',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '1rem',
                                }}
                            >
                                <span
                                    className={`badge badge-${result.sentiment === 'positive' ? 'positive' : result.sentiment === 'negative' ? 'negative' : 'neutral'}`}
                                    style={{ minWidth: '80px', justifyContent: 'center' }}
                                >
                                    {result.sentiment}
                                </span>
                                <span
                                    style={{
                                        fontWeight: 600,
                                        color: 'var(--accent-purple)',
                                        minWidth: '50px',
                                    }}
                                >
                                    {(result.confidence * 100).toFixed(0)}%
                                </span>
                                <span
                                    style={{
                                        flex: 1,
                                        color: 'var(--text-secondary)',
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                    }}
                                >
                                    {texts.split('\n')[index]?.substring(0, 100)}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default BatchAnalysis;
