import { X } from "lucide-react";
import { Detection } from "../context/AppContext";
import { useState } from "react";

interface ThresholdConfigModalProps {
  product: Detection;
  onClose: () => void;
}

interface ThresholdSettings {
  good: number;
  warning: number;
  critical: number;
}

export const ThresholdConfigModal = ({
  product,
  onClose,
}: ThresholdConfigModalProps) => {
  const [stockThresholds, setStockThresholds] = useState<ThresholdSettings>({
    good: 70,
    warning: 40,
    critical: 20,
  });

  const [qualityThresholds, setQualityThresholds] = useState<ThresholdSettings>(
    {
      good: 80,
      warning: 60,
      critical: 40,
    }
  );

  const [organizationThresholds, setOrganizationThresholds] =
    useState<ThresholdSettings>({
      good: 75,
      warning: 50,
      critical: 30,
    });

  const [contextThresholds, setContextThresholds] = useState<ThresholdSettings>(
    {
      good: 75,
      warning: 50,
      critical: 30,
    }
  );

  const handleSave = () => {
    console.log("Saving thresholds:", {
      product: product.product_name,
      stock: stockThresholds,
      quality: qualityThresholds,
      organization: organizationThresholds,
      context: contextThresholds,
    });
    onClose();
  };

  // Helper to render sliders with color gradient
  const Slider = ({
    label,
    thresholds,
    setThresholds,
    currentValue,
    colors,
  }: {
    label: string;
    thresholds: ThresholdSettings;
    setThresholds: (value: ThresholdSettings) => void;
    currentValue: number;
    colors: { good: string; warning: string; critical: string };
  }) => {
    const createGradient = (value: number, color: string) =>
      `linear-gradient(to right, ${color} 0%, ${color} ${value}%, #e5e7eb ${value}%, #e5e7eb 100%)`;

    return (
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-semibold text-gray-700">{label}</h4>
          <span className="text-sm text-gray-600">
            Atual: {currentValue}%
          </span>
        </div>
        <div className="space-y-3">
          {(["good", "warning", "critical"] as const).map((key) => (
            <div key={key}>
              <label className="flex justify-between text-xs text-gray-600 mb-1">
                <span>
                  {key.charAt(0).toUpperCase() + key.slice(1)}{" "}
                  {key === "good"
                    ? "(above)"
                    : key === "warning"
                    ? "(above)"
                    : "(below)"}
                </span>
                <span className={`font-medium`} style={{ color: colors[key] }}>
                  {thresholds[key]}%
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={thresholds[key]}
                onChange={(e) =>
                  setThresholds({
                    ...thresholds,
                    [key]: parseInt(e.target.value),
                  })
                }
                className="w-full h-2 rounded-lg cursor-pointer"
                style={{
                  background: createGradient(thresholds[key], colors[key]),
                }}
              />
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-start">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-1">
              Configurações de Alerta
            </h2>
            <p className="text-sm text-gray-600">{product.product_name}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              Defina valores limite para determinar quando os alertas devem ser acionados para
              este produto. Valores acima de «Bom» serão exibidos como saudáveis, entre
              «Aviso» e «Bom» como cautelares e abaixo de «Crítico» como
              requerendo atenção imediata.
            </p>
          </div>

          <Slider
            label="Níveis de estoque"
            thresholds={stockThresholds}
            setThresholds={setStockThresholds}
            currentValue={product.quantidade_pct}
            colors={{
              good: "#16a34a",
              warning: "#facc15",
              critical: "#dc2626",
            }}
          />

          <Slider
            label="Qualidade"
            thresholds={qualityThresholds}
            setThresholds={setQualityThresholds}
            currentValue={product.qualidade_pct}
            colors={{
              good: "#16a34a",
              warning: "#facc15",
              critical: "#dc2626",
            }}
          />

          <Slider
            label="Organização"
            thresholds={organizationThresholds}
            setThresholds={setOrganizationThresholds}
            currentValue={product.organizacao_pct}
            colors={{
              good: "#16a34a",
              warning: "#facc15",
              critical: "#dc2626",
            }}
          />

          <Slider
            label="Contexto (iluminação e limpeza)"
            thresholds={contextThresholds}
            setThresholds={setContextThresholds}
            currentValue={product.contexto_pct}
            colors={{
              good: "#16a34a",
              warning: "#facc15",
              critical: "#dc2626",
            }}
          />

          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Guardar Definições
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

