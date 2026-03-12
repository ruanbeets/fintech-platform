import { useState, useEffect } from "react";

export default function ThemeToggle() {

  const [theme, setTheme] = useState("dark");

  useEffect(() => {

    const saved = localStorage.getItem("theme");

    if (saved) {
      setTheme(saved);
      document.documentElement.classList.toggle(
        "dark",
        saved === "dark"
      );
    }

  }, []);

  const toggleTheme = () => {

    const newTheme =
      theme === "dark" ? "light" : "dark";

    setTheme(newTheme);

    localStorage.setItem("theme", newTheme);

    document.documentElement.classList.toggle(
      "dark",
      newTheme === "dark"
    );

  };

  return (

    <div>

      <label className="block text-sm text-gray-400 mb-2">
        Theme
      </label>

      <button
        onClick={toggleTheme}
        className="bg-gray-800 border border-gray-700 px-4 py-2 rounded"
      >
        Toggle Theme
      </button>

    </div>

  );

}