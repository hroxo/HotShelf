import { X } from "lucide-react";

const LiveViewModal = ({ imageSrc, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[9999]">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 relative max-w-4xl w-full mx-4">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          <X size={20} />
        </button>

        <h2 className="text-xl font-semibold mb-4 dark:text-white">Visão em Direto</h2>

        <img
          src={imageSrc}
          alt="Live View"
          className="w-full rounded-lg border dark:border-gray-700 object-contain max-h-[70vh]"
        />
      </div>
    </div>
  );
};

export default LiveViewModal;
