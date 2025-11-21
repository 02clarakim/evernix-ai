// components/AgentCard.jsx
"use client";

export default function AgentCard({ name, description, selected, onSelect }) {
  return (
    <div
      onClick={onSelect}
      className={`
        cursor-pointer p-6 rounded-lg border transition
        hover:shadow-md

        ${selected
          ? `
            border-blue-700 bg-blue-50
            dark:border-blue-500 dark:bg-blue-900/30
          `
          : `
            border-gray-300 hover:border-gray-500
            dark:border-gray-700 dark:hover:border-gray-500
            dark:bg-gray-800
          `}
      `}
    >
      <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">
        {name}
      </h2>
      <p className="text-gray-600 dark:text-gray-300 text-sm">
        {description}
      </p>
    </div>
  );
}
