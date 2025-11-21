"use client";

import { useState } from "react";

export default function UniverseSelector({ onChange }) {
  const stockOptions = ["AAPL", "MSFT", "KO", "BAC", "JNJ", "PG", "AMZN", "UBER", "GOOG", "AXP", "NVR", "UNH"];
  const [selected, setSelected] = useState([]);

  const toggleStock = (symbol) => {
    let updated;
    if (selected.includes(symbol)) {
      updated = selected.filter((s) => s !== symbol);
    } else {
      updated = [...selected, symbol];
    }
    setSelected(updated);
    onChange(updated);
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">
        Choose Universe
      </h3>

      <div className="grid grid-cols-3 gap-4">
        {stockOptions.map((s) => {
          const isSelected = selected.includes(s);

          return (
            <button
              key={s}
              onClick={() => toggleStock(s)}
              className={`
                px-4 py-2 border rounded-lg transition hover:shadow-sm
                ${
                  isSelected
                    ? `
                      bg-blue-600 text-white border-blue-600 
                      dark:bg-blue-500 dark:border-blue-500
                    `
                    : `
                      bg-white text-gray-800 border-gray-300
                      dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600
                    `
                }
              `}
            >
              {s}
            </button>
          );
        })}
      </div>
    </div>
  );
}
