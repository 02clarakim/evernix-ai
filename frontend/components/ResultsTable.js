"use client";
import { useState, Fragment } from "react";

export default function ResultsTable({ results, csvFile }) {
  const [expandedRows, setExpandedRows] = useState(new Set());

  if (!results || !Array.isArray(results) || results.length === 0) return null;

  const mainColumns = ["symbol", "Company", "sector", "action", "confidence", "score", "rationale"];
  const allColumns = Object.keys(results[0]);
  const extraColumns = allColumns.filter((col) => !mainColumns.includes(col));

  const toggleRow = (symbol) => {
    const newSet = new Set(expandedRows);
    newSet.has(symbol) ? newSet.delete(symbol) : newSet.add(symbol);
    setExpandedRows(newSet);
  };

  const handleDownload = () => {
    if (!csvFile) return;
    window.open(`http://localhost:8000/download/${csvFile}`, "_blank");
  };

  const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  // Action color → include dark versions
  const actionColor = (action) => {
    switch ((action || "").toUpperCase()) {
      case "BUY":
        return "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200 font-semibold";
      case "HOLD":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-200 font-semibold";
      case "SELL":
        return "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200 font-semibold";
      default:
        return "";
    }
  };

  return (
    <div className="mt-10">
      <div className="overflow-x-auto">
        <table className="
          min-w-full border border-gray-300 dark:border-gray-700
          text-gray-900 dark:text-gray-100
        ">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-800">
              <th className="px-4 py-2 border dark:border-gray-700"></th>
              {mainColumns.map((h) => (
                <th
                  key={h}
                  className="px-4 py-2 border text-left dark:border-gray-700"
                >
                  {capitalize(h)}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {results.map((row, i) => (
              <Fragment key={row.symbol || i}>
                <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/60">
                  <td
                    className="px-4 py-2 border cursor-pointer select-none dark:border-gray-700"
                    onClick={() => toggleRow(row.symbol)}
                  >
                    {expandedRows.has(row.symbol) ? "▼" : "▶"}
                  </td>

                  {mainColumns.map((h) => (
                    <td
                      key={h}
                      className={`
                        px-4 py-2 border dark:border-gray-700
                        ${h === "action" ? actionColor(row[h]) : ""}
                      `}
                    >
                      {row[h] != null ? row[h].toString() : ""}
                    </td>
                  ))}
                </tr>

                {expandedRows.has(row.symbol) && extraColumns.length > 0 && (
                  <tr className="bg-gray-50 dark:bg-gray-900/40">
                    <td></td>
                    <td colSpan={mainColumns.length} className="border-x dark:border-gray-700">
                      <div className="grid grid-cols-2 gap-4 p-2 text-sm">
                        {extraColumns.map((col) => (
                          <div key={col}>
                            <strong>{capitalize(col)}:</strong>{" "}
                            {row[col] != null ? row[col].toString() : ""}
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {csvFile && (
        <div className="text-right mt-4">
          <button
            onClick={handleDownload}
            className="
              px-4 py-2 rounded 
              bg-green-600 text-white hover:bg-green-700
              dark:bg-green-700 dark:hover:bg-green-600
            "
          >
            Download CSV
          </button>
        </div>
      )}
    </div>
  );
}
