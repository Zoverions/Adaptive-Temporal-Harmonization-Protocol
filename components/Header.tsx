
import React from 'react';
import { APP_TITLE, APP_SUBTITLE } from '../constants';

const Header: React.FC = () => {
  return (
    <header className="text-center mb-8 md:mb-12">
      <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-violet-500 animate-pulse">
        {APP_TITLE}
      </h1>
      <p className="text-slate-400 mt-2 text-md sm:text-lg font-mono tracking-wider">
        {APP_SUBTITLE}
      </p>
    </header>
  );
};

export default Header;
