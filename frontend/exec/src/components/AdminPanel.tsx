import { X } from "lucide-react";

export default function AdminPanel({
  currentUser,
  onClose,
  onSwitchUser,
  onUpdatePhoto,
}: {
  currentUser: any;
  onClose: () => void;
  onSwitchUser: (role: "worker" | "administrator") => void;
  onUpdatePhoto: (url: string) => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold dark:text-white">
            Painel de Utilizador
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400"
          >
            <X size={24} />
          </button>
        </div>

        <div className="flex flex-col items-center mb-6">
          <img
            src={currentUser.photo}
            alt={currentUser.name}
            className="w-24 h-24 rounded-full mb-4"
          />
          <h3 className="text-xl font-semibold dark:text-white">
            {currentUser.name}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">{currentUser.role}</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2 dark:text-white">
              Mudar Perfil
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => onSwitchUser("worker")}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Trabalhador
              </button>
              <button
                onClick={() => onSwitchUser("administrator")}
                className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                Administrador
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
