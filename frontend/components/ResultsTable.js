"use client";

import { useState, Fragment } from "react";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";

export default function ResultsTable({ results, csvFile }) {
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [generatingRows, setGeneratingRows] = useState(new Set());

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

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  const handleFullReport = async (symbol) => {
    const newSet = new Set(generatingRows);
    newSet.add(symbol);
    setGeneratingRows(newSet);

    try {
      const res = await fetch(`${apiUrl}/generate_full_report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ universe: [symbol] }),
      });

      if (!res.ok) throw new Error("Failed to generate report");

      // Open new window and inject the styled HTML (which now includes the download icon)
      const html = await res.text();
      const win = window.open("", "_blank");
      win.document.write(html);
      win.document.close();
    } catch (err) {
      console.error("Full report generation failed:", err);
      alert("Failed to generate full report.");
    } finally {
      const newSet2 = new Set(generatingRows);
      newSet2.delete(symbol);
      setGeneratingRows(newSet2);
    }
  };

  return (
    <div className="mt-10">
      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-800">
              <th className="px-4 py-2 border dark:border-gray-700"></th>
              {mainColumns.map((h) => (
                <th key={h} className="px-4 py-2 border text-left dark:border-gray-700">
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
                      className={`px-4 py-2 border dark:border-gray-700 ${
                        h === "action" ? actionColor(row[h]) : ""
                      } ${h === "rationale" ? "break-words max-w-xs" : ""}`}
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

                      {/* Small Link-Style Full Report Button */}
                      <div className="flex justify-start mt-2 mb-2 pl-2">
                        <button
                          onClick={() => handleFullReport(row.symbol)}
                          disabled={generatingRows.has(row.symbol)}
                          className={`flex items-center gap-1 text-sm font-medium transition ${
                            generatingRows.has(row.symbol)
                              ? "text-gray-400 cursor-not-allowed"
                              : "text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                          }`}
                        >
                          {generatingRows.has(row.symbol) ? "Generating..." : "Generate Full Report"}
                          {!generatingRows.has(row.symbol) && (
                            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
                          )}
                        </button>
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
            className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600"
          >
            Download CSV
          </button>
        </div>
      )}
    </div>
  );
}
