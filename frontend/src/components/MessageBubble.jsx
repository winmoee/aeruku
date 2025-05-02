import React, { memo } from "react";

const MessageBubble = memo(({ message, fallback = "", isUser = false }) => {
    const displayText = message.response?.trim() ? message.response : fallback;

    if (displayText.startsWith("###")) {
        return null;
    }

    const renderTextWithLinks = (text) => {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const parts = text.split(urlRegex);

        return parts.map((part, index) => {
            if (urlRegex.test(part)) {
                return (
                    <a
                        key={index}
                        href={part}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:text-blue-600 underline"
                        aria-label={`External link to ${part}`}
                    >
                        {part}
                    </a>
                );
            }
            return part;
        });
    };

    return (
        <div
            className={`
                inline-block px-4 py-2 mb-1 rounded-lg shadow-sm
                ${isUser 
                    ? "ml-auto bg-primary-600 text-white dark:bg-primary-500" 
                    : "mr-auto bg-white dark:bg-dark-800 border border-gray-200 dark:border-gray-700"
                }
                break-words max-w-[75%] transition-colors duration-200
            `}
            role="article"
            aria-label={`${isUser ? 'User' : 'Agent'} message`}
        >
            {renderTextWithLinks(displayText)}
        </div>
    );
});

MessageBubble.displayName = 'MessageBubble';

export default MessageBubble;
