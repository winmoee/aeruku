import React, { memo } from "react";

const NavBar = memo(({ title }) => {
    return (
        <header 
            className="fixed top-0 left-0 w-full p-4 bg-white/80 dark:bg-dark-900/80 
                backdrop-blur-lg shadow-lg z-10 flex justify-between items-center
                transition-colors duration-200 border-b border-gray-200 dark:border-gray-700"
            role="banner"
        >
            <h1 className="text-2xl font-bold font-display bg-gradient-to-r from-primary-600 to-primary-400 
                bg-clip-text text-transparent">
                {title || 'Aeruku'}
            </h1>
        </header>
    );
});

NavBar.displayName = 'NavBar';

export default NavBar;
