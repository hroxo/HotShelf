import { Sun, Moon } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Header({
  currentUser,
  isDarkMode,
  onToggleDarkMode,
  onOpenAdminPanel,
}: {
  currentUser: { name: string; role: string; photo: string };
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  onOpenAdminPanel: () => void;
}) {
  const navigate = useNavigate();

  return (
    <div className="bg-[#D91E2A] text-white px-6 py-4 flex items-center justify-between">
      <div
        onClick={() => navigate("/")}
        className="flex flex-col items-start cursor-pointer"
      >
        <div className="text-2xl font-bold">Hot Shelf</div>
        <div className="text-xs font-extralight">
          powered by The 42 Ducks driven to SONAE
        </div>
      </div>

      <div className="text-lg">Loja: 1410 | Leiria - São Romão</div>

      <div className="flex items-center gap-4">
        <span className="text-sm">Olá, {currentUser.name}</span>

        <button
          onClick={onToggleDarkMode}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <button
          onClick={onOpenAdminPanel}
          className="flex items-center gap-2 hover:bg-white/10 px-3 py-2 rounded-lg transition-colors"
        >
          <img
            src={currentUser.photo}
            alt={currentUser.name}
            className="w-8 h-8 rounded-full"
          />
          <span className="text-sm">{currentUser.name}</span>
        </button>
      </div>
    </div>
  );
}
