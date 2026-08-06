"use client";

import { useRef, useState, type DragEvent } from "react";

interface DropzoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
}

export function Dropzone({ files, onFilesChange }: DropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  function addFiles(list: FileList | null) {
    if (!list) return;
    const csvFiles = Array.from(list).filter((f) => f.name.toLowerCase().endsWith(".csv"));
    if (csvFiles.length) onFilesChange([...files, ...csvFiles]);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
    addFiles(event.dataTransfer.files);
  }

  function removeFile(index: number) {
    onFilesChange(files.filter((_, i) => i !== index));
  }

  return (
    <div className="space-y-2">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-lg border border-dashed px-3 py-2 text-center text-xs transition ${
          dragActive
            ? "border-neutral-500 bg-neutral-100 text-neutral-700"
            : "border-neutral-300 text-neutral-400 hover:border-neutral-400 hover:text-neutral-500"
        }`}
      >
        Drop CSVs here, or click to browse
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          multiple
          className="hidden"
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>
      {files.length > 0 && (
        <ul className="flex flex-wrap gap-1.5">
          {files.map((file, index) => (
            <li
              key={`${file.name}-${index}`}
              className="flex items-center gap-1.5 rounded-full bg-neutral-100 px-2.5 py-1 text-xs text-neutral-700"
            >
              {file.name}
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="text-neutral-400 hover:text-neutral-700"
                aria-label={`Remove ${file.name}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
