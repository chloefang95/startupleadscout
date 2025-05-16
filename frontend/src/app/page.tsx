"use client";

import { useState } from "react";
import axios from "axios";

interface ResearchResult {
  summary: string;
  sentiment: string;
  pain_points: string[];
  suggested_features: string[];
}

export default function Home() {
  const [idea, setIdea] = useState("");
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await axios.post("http://localhost:8000/research", { idea });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-center">StartupLeadScout</h1>
        <form onSubmit={handleSubmit} className="mb-6 flex flex-col gap-4">
          <label htmlFor="idea" className="font-semibold">Enter your startup idea:</label>
          <input
            id="idea"
            type="text"
            value={idea}
            onChange={e => setIdea(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="e.g. smart pet collar"
            required
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
            disabled={loading}
          >
            {loading ? "Researching..." : "Research"}
          </button>
        </form>
        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>
        )}
        {result && (
          <div className="space-y-4">
            <div>
              <h2 className="font-semibold text-lg mb-1">Summary</h2>
              <p className="bg-gray-100 rounded p-3">{result.summary}</p>
            </div>
            <div>
              <h2 className="font-semibold text-lg mb-1">Sentiment</h2>
              <p className="bg-gray-100 rounded p-3">{result.sentiment}</p>
            </div>
            <div>
              <h2 className="font-semibold text-lg mb-1">Pain Points</h2>
              <ul className="bg-gray-100 rounded p-3 list-disc list-inside">
                {result.pain_points.map((point, idx) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="font-semibold text-lg mb-1">Suggested Features</h2>
              <ul className="bg-gray-100 rounded p-3 list-disc list-inside">
                {result.suggested_features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
