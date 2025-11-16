import { X } from "lucide-react";
import { useAppContext } from "../context/AppContext";

export function ProductDetailsModal() {
  const { selectedSlot, setSelectedSlot } = useAppContext();

  if (!selectedSlot) return null;

  const metrics = [
    {
      label: "Estoque",
      value: selectedSlot.quantidade_pct,
      description: "O quão cheio a secção está",
      color: "blue",
    },
    {
      label: "Qualidade",
      value: selectedSlot.qualidade_pct,
      description: "Condição do produto",
      color: "green",
    },
    {
      label: "Organização",
      value: selectedSlot.organizacao_pct,
      description: "Qualidade da organização",
      color: "purple",
    },
    {
      label: "Context",
      value: selectedSlot.contexto_pct,
      description: "Condições ambientais (iluminação, limpeza)",
      color: "orange",
    },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-1">
              {selectedSlot.product_name}
            </h2>
            <p className="text-sm text-gray-600">ROI: {selectedSlot.roi_id}</p>
          </div>
          <button
            onClick={() => setSelectedSlot(null)}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                Overall Attractiveness
              </span>
              <span className="text-2xl font-bold text-gray-900">
                {selectedSlot.score}%
              </span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  selectedSlot.score >= 70
                    ? "bg-green-600"
                    : selectedSlot.score >= 40
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${selectedSlot.score}%` }}
              />
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Métricas Detalhadas
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {metrics.map((metric) => (
                <div
                  key={metric.label}
                  className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-1">
                        {metric.label}
                      </div>
                      <div className="text-xs text-gray-500">
                        {metric.description}
                      </div>
                    </div>
                    <div className="text-xl font-bold text-gray-900">
                      {metric.value}%
                    </div>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        metric.color === "blue"
                          ? "bg-blue-500"
                          : metric.color === "green"
                          ? "bg-green-500"
                          : metric.color === "purple"
                          ? "bg-purple-500"
                          : "bg-orange-500"
                      }`}
                      style={{ width: `${metric.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">
              Perspectivas
            </h4>
            <p className="text-sm text-gray-600">{selectedSlot.insights}</p>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-gray-600">Confiança: </span>
                <span className="font-semibold text-gray-900">
                  {(selectedSlot.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                <span className="text-gray-600">Índice de variância: </span>
                <span className="font-semibold text-gray-900">
                  {selectedSlot.indice_var}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
