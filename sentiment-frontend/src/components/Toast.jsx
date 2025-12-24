import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';

const Toast = ({ message, type = 'success', onClose }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Trigger enter animation
        requestAnimationFrame(() => setIsVisible(true));

        // Auto close
        const timer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
        }, 3700);

        return () => clearTimeout(timer);
    }, [onClose]);

    const getConfig = () => {
        switch (type) {
            case 'success':
                return {
                    icon: CheckCircle,
                    bgColor: 'var(--success-50)',
                    borderColor: 'var(--success-200)',
                    iconColor: 'var(--success-500)',
                    textColor: 'var(--success-800)',
                };
            case 'error':
                return {
                    icon: XCircle,
                    bgColor: 'var(--danger-50)',
                    borderColor: 'var(--danger-200)',
                    iconColor: 'var(--danger-500)',
                    textColor: 'var(--danger-800)',
                };
            default:
                return {
                    icon: AlertCircle,
                    bgColor: 'var(--warning-50)',
                    borderColor: 'var(--warning-200)',
                    iconColor: 'var(--warning-500)',
                    textColor: 'var(--warning-800)',
                };
        }
    };

    const config = getConfig();
    const Icon = config.icon;

    return (
        <div
            style={{
                position: 'fixed',
                bottom: '2rem',
                right: '2rem',
                zIndex: 1000,
                transform: isVisible ? 'translateX(0)' : 'translateX(120%)',
                opacity: isVisible ? 1 : 0,
                transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
            }}
        >
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '1rem 1.25rem',
                    background: config.bgColor,
                    border: `1px solid ${config.borderColor}`,
                    borderRadius: 'var(--radius-xl)',
                    boxShadow: 'var(--shadow-lg)',
                    maxWidth: '400px',
                }}
            >
                <Icon size={20} style={{ color: config.iconColor, flexShrink: 0 }} />
                <span style={{ color: config.textColor, fontWeight: 500, fontSize: '0.9375rem' }}>
                    {message}
                </span>
                <button
                    onClick={() => {
                        setIsVisible(false);
                        setTimeout(onClose, 300);
                    }}
                    style={{
                        background: 'none',
                        border: 'none',
                        padding: '4px',
                        cursor: 'pointer',
                        color: config.iconColor,
                        opacity: 0.7,
                        marginLeft: '0.5rem',
                        flexShrink: 0,
                    }}
                >
                    <X size={16} />
                </button>
            </div>
        </div>
    );
};

export default Toast;
