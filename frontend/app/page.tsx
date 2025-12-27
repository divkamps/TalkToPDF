"use client";

import { useState } from "react";

export default function Home() {
  const [docId, setDocId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function uploadPdf(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/pdf/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setDocId(data.doc_id);
    setLoading(false);
  }

  async function askQuestion() {
    if (!docId || !question) return;

    setLoading(true);

    const res = await fetch(`http://127.0.0.1:8000/pdf/${docId}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    setAnswer(data);
    setLoading(false);
  }

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">TalkToPDF</h1>

      {/* Upload */}
      <div className="mb-6">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => {
            if (e.target.files) uploadPdf(e.target.files[0]);
          }}
        />
        {docId && (
          <p className="text-sm text-green-600 mt-2">
            PDF uploaded successfully
          </p>
        )}
      </div>

      {/* Question */}
      {docId && (
        <div className="mb-6">
          <textarea
            className="w-full border p-2"
            placeholder="Ask a question about the PDF..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button
            onClick={askQuestion}
            className="mt-2 px-4 py-2 bg-black text-white"
          >
            Ask
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && <p>Loading...</p>}

      {/* Answer */}
      {answer && (
        <div className="mt-6">
          <h2 className="font-semibold">Answer</h2>
          <p className="mt-2">{answer.answer}</p>

          {answer.citations?.length > 0 && (
            <>
              <h3 className="font-semibold mt-4">Citations</h3>
              <ul className="text-sm mt-2">
                {answer.citations.map((c: any, i: number) => (
                  <li key={i} className="mb-2">
                    <strong>Page {c.page}:</strong> {c.snippet}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </main>
  );
}
