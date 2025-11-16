import { useParams } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import { Video, Package, MoreVertical } from "lucide-react";
import { useState } from "react";
import { ThresholdConfigModal } from "../components/ThresholdConfigModal";
import { ProductDetailsModal } from "../components/ProductDetailsModal";
import LiveViewModal from "../components/LiveViewModal";

const ShelfDetail = () => {
  const { cameraId } = useParams();
  const {
    detections,
    currentUser,
    setSelectedSlot,
    selectedSlot,
    setSelectedThresholdProduct,
    openThresholdModal,
    thresholdModalProduct,
    closeThresholdModal,
  } = useAppContext();

  const [showLiveView, setShowLiveView] = useState(false);

  const shelfDetections = detections.filter(
    (d) =>
      d.camera_id === cameraId ||
      d.roi_id === cameraId ||
      d.product_id === cameraId
  );

  const sortedDetections = [...shelfDetections].sort((a, b) => {
    const aTopLeft = a.quad?.[0] ?? [0, 0];
    const bTopLeft = b.quad?.[0] ?? [0, 0];

    const aY = aTopLeft[1];
    const bY = bTopLeft[1];

    if (Math.abs(aY - bY) > 50) return aY - bY;

    return aTopLeft[0] - bTopLeft[0];
  });

  const sortedByPriority = [...shelfDetections]
    .filter((detection) => detection.score <= 50)
    .sort((a, b) => a.score - b.score);

  if (sortedDetections.length === 0) {
    return (
      <div className="p-10 text-center text-gray-600 dark:text-gray-300">
        <h2 className="text-2xl font-semibold mb-2">No data found</h2>
        <p>There are no shelf detections for ID: {cameraId}</p>
      </div>
    );
  }

  return (
    <div className="p-6 flex flex-col md:flex-row gap-6 min-h-screen overflow-hidden">
      {thresholdModalProduct && (
        <ThresholdConfigModal
          product={detections.find((d) => d.product_name === thresholdModalProduct)!}
          onClose={closeThresholdModal}
        />
      )}

      {selectedSlot && <ProductDetailsModal />}

      {/* LIVE VIEW MODAL */}
      {showLiveView && (
        <LiveViewModal
          imageSrc={new URL(`../media/${cameraId}.jpg`, import.meta.url).href}
          onClose={() => setShowLiveView(false)}
        />
      )}

      {/* LEFT COLUMN */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg flex flex-col min-h-[78vh] overflow-hidden">
          <h2 className="text-2xl font-bold dark:text-white mb-4">
            Visão em Grelha <span className="text-gray-500">({cameraId})</span>
          </h2>

          {/* GRID */}
          <div className="grid grid-cols-3 md:grid-cols-4 gap-4 overflow-y-auto pr-2 flex-1">
            {sortedDetections.map((detection) => {
              const bgColor =
                detection.score >= 70
                  ? "bg-green-100 dark:bg-green-900/40"
                  : detection.score >= 50
                  ? "bg-yellow-100 dark:bg-yellow-900/40"
                  : "bg-red-100 dark:bg-red-900/40";

              return (
                <div
                  key={detection.roi_id}
                  onClick={() => setSelectedSlot(detection)}
                  className={`${bgColor} rounded-lg p-4 cursor-pointer hover:shadow-xl transition-all border dark:border-gray-700 flex flex-col justify-between`}
                >
                  <div>
                    <div className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      {detection.product_name}
                    </div>
                  </div>

                  <div className="mt-auto pt-3 border-t border-gray-300 dark:border-gray-700">
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Estoque:</span>
                        <span className="font-semibold">{detection.quantidade_pct}%</span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Pontuação:</span>
                        <span className="font-semibold">{detection.score}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* LIVE VIEW BUTTON */}
        <div className="flex w-full mt-4">
          <button
            onClick={() => setShowLiveView(true)}
            className="bg-[#D91E2A] w-full text-white py-2 rounded-lg flex items-center justify-center gap-2 hover:bg-[#B91825] transition-colors text-sm shadow-md"
          >
            <Video size={18} />
            Visão em Direto
          </button>
        </div>
      </div>

      {/* RIGHT SIDEBAR */}
      <div className="w-full md:w-96 flex flex-col overflow-hidden">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg flex flex-col min-h-[78vh] overflow-hidden">
          <h2 className="text-xl font-bold dark:text-white mb-4">Produtos em alerta</h2>

          <div className="space-y-4 overflow-y-auto pr-2 flex-1">
            {sortedByPriority.map((product) => (
              <div
                key={product.product_id}
                className="border dark:border-gray-700 rounded-lg p-4 relative bg-gray-50 dark:bg-gray-900/40"
              >
                {currentUser.role === "administrator" && (
                  <button
                    onClick={() => {
                      openThresholdModal(product.product_name);
                      setSelectedThresholdProduct(product.product_name);
                    }}
                    className="absolute top-2 right-2 p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                  >
                    <MoreVertical size={18} />
                  </button>
                )}

                <div className="flex items-center gap-3 mb-3">
                  <Package size={28} className="text-gray-500 dark:text-gray-300" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-sm dark:text-white">
                      {product.product_name}
                    </h3>

                    <span
                      className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${
                        product.score >= 70
                          ? "bg-green-100 text-green-800"
                          : product.score >= 50
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {product.score >= 70
                        ? "Bom"
                        : product.score >= 50
                        ? "Razoável"
                        : "Mau"}
                    </span>
                  </div>
                </div>

                {/* Bars */}
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-600 dark:text-gray-400">Estoque</span>
                      <span className="font-semibold dark:text-white">
                        {product.quantidade_pct}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded-full">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${product.quantidade_pct}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-600 dark:text-gray-400">Atratividade</span>
                      <span className="font-semibold dark:text-white">{product.score}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded-full">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${product.score}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
};

export default ShelfDetail;
