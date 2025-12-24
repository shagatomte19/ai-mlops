import React from 'react';
import { Sparkles, Moon, Sun, Download, Wifi, WifiOff } from 'lucide-react';

const Header = ({ theme, onThemeToggle, onExport, isConnected }) => {
    return (
        <header
            className="glass-card"
            style={{
                position: 'sticky',
                top: '1rem',
                margin: '1rem',
                padding: '1rem 1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                zIndex: 100,
                borderRadius: 'var(--radius-2xl)',
            }}
        >
            {/* Logo */}
            <div className="flex items-center gap-4">
                <div
                    style={{
                        width: 44,
                        height: 44,
                        borderRadius: 'var(--radius-xl)',
                        background: 'var(--accent-gradient)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: 'var(--shadow-glow)',
                    }}
                >
                    <Sparkles size={22} color="white" />
                </div>
                <div>
                    <h1 style={{
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        lineHeight: 1.2
                    }}>
                        SentimentAI
                    </h1>
                    <span className="text-small">v2.0</span>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
                {/* Connection Status */}
                <div
                    className="flex items-center gap-2"
                    style={{
                        padding: '0.5rem 1rem',
                        borderRadius: 'var(--radius-lg)',
                        background: isConnected ? 'var(--success-100)' : 'var(--danger-100)',
                        color: isConnected ? 'var(--success-700)' : 'var(--danger-700)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                    }}
                >
                    {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
                    <span className="hide-mobile">
                        {isConnected ? 'Connected' : 'Offline'}
                    </span>
                </div>

                {/* Export Button */}
                <div style={{ position: 'relative' }} className="dropdown-container">
                    <button
                        className="btn btn-secondary btn-icon"
                        onClick={() => document.getElementById('export-menu').classList.toggle('show')}
                        title="Export Data"
                    >
                        <Download size={18} />
                    </button>
                    <div
                        id="export-menu"
                        className="glass-card"
                        style={{
                            position: 'absolute',
                            top: '100%',
                            right: 0,
                            marginTop: '0.5rem',
                            padding: '0.5rem',
                            display: 'none',
                            minWidth: '120px',
                        }}
                    >
                        <button
                            onClick={() => {
                                onExport('json');
                                document.getElementById('export-menu').classList.remove('show');
                            }}
                            style={{
                                display: 'block',
                                width: '100%',
                                padding: '0.5rem 1rem',
                                textAlign: 'left',
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.875rem',
                                color: 'var(--text-primary)',
                            }}
                            onMouseEnter={(e) => e.target.style.background = 'var(--neutral-100)'}
                            onMouseLeave={(e) => e.target.style.background = 'none'}
                        >
                            Export JSON
                        </button>
                        <button
                            onClick={() => {
                                onExport('csv');
                                document.getElementById('export-menu').classList.remove('show');
                            }}
                            style={{
                                display: 'block',
                                width: '100%',
                                padding: '0.5rem 1rem',
                                textAlign: 'left',
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.875rem',
                                color: 'var(--text-primary)',
                            }}
                            onMouseEnter={(e) => e.target.style.background = 'var(--neutral-100)'}
                            onMouseLeave={(e) => e.target.style.background = 'none'}
                        >
                            Export CSV
                        </button>
                    </div>
                </div>

                {/* Theme Toggle */}
                <button
                    className="btn btn-secondary btn-icon"
                    onClick={onThemeToggle}
                    title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
                >
                    {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
                </button>
            </div>

            <style>{`
        #export-menu.show {
          display: block !important;
          animation: fadeIn 0.2s ease-out;
        }
      `}</style>
        </header>
    );
};

export default Header;
