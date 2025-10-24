
import React from 'react';

interface SectionTitleProps {
  title: string;
  subtitle?: string;
}

const SectionTitle: React.FC<SectionTitleProps> = ({ title, subtitle }) => {
  return (
    <div className="mb-6">
      <h2 className="text-2xl md:text-3xl font-bold text-gray-100">{title}</h2>
      {subtitle && <p className="text-slate-400 font-mono text-sm">{subtitle}</p>}
      <div className="mt-2 h-0.5 w-20 bg-gradient-to-r from-cyan-500 to-violet-500"></div>
    </div>
  );
};

export default SectionTitle;
