"use client";

export default function Header() {
  return (
    <header className="h-14 border-b border-gray-200 bg-white flex items-center px-6 shrink-0">
      <h1 className="text-lg font-semibold text-gray-800">Legal AI Assistant</h1>
      <span className="ml-3 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
        MVP
      </span>
    </header>
  );
}
