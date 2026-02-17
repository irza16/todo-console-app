import { useState, KeyboardEvent } from "react";

interface TagsInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
}

export function TagsInput({ value, onChange }: TagsInputProps) {
  const [inputValue, setInputValue] = useState("");

  const addTag = () => {
    if (inputValue.trim() && !value.includes(inputValue.trim())) {
      onChange([...value, inputValue.trim()]);
      setInputValue("");
    }
  };

  const removeTag = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag();
    } else if (e.key === "Backspace" && inputValue === "" && value.length > 0) {
      // Remove last tag when backspace is pressed on empty input
      const newTags = [...value];
      newTags.pop();
      onChange(newTags);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1 mb-1">
        {value.map((tag, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(index)}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type tag and press Enter..."
        className="w-full border rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 bg-background"
      />
    </div>
  );
}