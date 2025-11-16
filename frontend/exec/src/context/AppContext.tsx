import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { getShelfs } from "../api/shelfs";

export type Detection = {
  id: string;
  camera_id: string;
  image_name: string;
  roi_id: string;
  product_id: string;
  product_name: string;
  fruit_type: string;
  quantidade_pct: number;
  qualidade_pct: number;
  organizacao_pct: number;
  contexto_pct: number;
  insights: string;
  confidence: number;
  roi_quad_px: {
    top_left: [number, number];
    top_right: [number, number];
    bottom_right: [number, number];
    bottom_left: [number, number];
  };
  pontuacao_total: number;
  indice_var: number;
};

type User = {
  name: string;
  role: "worker" | "administrator";
  photo: string;
};

type FilterType = "all" | "critical" | "alert";

type ShelfsState = {
  s6591?: Detection[];
  s6371?: Detection[];
  s6373?: Detection[];
};

type AppContextType = {
  shelfs: ShelfsState;
  detections: Detection[]; // combined for filtered view
  currentFilter: FilterType;
  setCurrentFilter: (filter: FilterType) => void;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  currentUser: User;
  switchUser: (role: "worker" | "administrator") => void;
  selectedSlot: Detection | null;
  setSelectedSlot: (d: Detection | null) => void;
  selectedThresholdProduct: string | null;
  setSelectedThresholdProduct: (p: string | null) => void;
  thresholdModalProduct: string | null;
  openThresholdModal: (productName: string) => void;
  closeThresholdModal: () => void;
  loading: boolean;
  error: string | null;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [shelfs, setShelfs] = useState<ShelfsState>({});
  const [detections, setDetections] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isDarkMode, setIsDarkMode] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<Detection | null>(null);
  const [selectedThresholdProduct, setSelectedThresholdProduct] = useState<string | null>(null);
  const [currentFilter, setCurrentFilter] = useState<FilterType>("all");
  const [thresholdModalProduct, setThresholdModalProduct] = useState<string | null>(null);

  const [currentUser, setCurrentUser] = useState<User>({
    name: "Trabalhador",
    role: "worker",
    photo: "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
  });

  const profiles = {
    worker: {
      name: "Trabalhador",
      role: "worker" as const,
      photo: "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
    },
    administrator: {
      name: "Administrador",
      role: "administrator" as const,
      photo: "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
    },
  };

  useEffect(() => {
    const fetchShelfs = async () => {
      try {
        setLoading(true);
        const data = await getShelfs();

        // Prepare shelfs object, skip shelves with no detections
        const newShelfs: ShelfsState = {};
        if (data.s6591?.detections) newShelfs.s6591 = data.s6591.detections;
        if (data.s6371?.detections) newShelfs.s6371 = data.s6371.detections;
        if (data.s6373?.detections) newShelfs.s6373 = data.s6373.detections;

        setShelfs(newShelfs);

        // Combine all detections for filtering
        setDetections(Object.values(newShelfs).flat());
      } catch (err) {
        console.error(err);
        setError("Failed to fetch detections");
      } finally {
        setLoading(false);
      }
    };

    fetchShelfs();
  }, []);

  function getDetectionStatus(d: Detection): "critical" | "alert" | "ok" {
    if (d.pontuacao_total < 50) return "critical";
    if (d.pontuacao_total < 75) return "alert";
    return "ok";
  }

  const filteredDetections = detections.filter((d) => {
    if (currentFilter === "all") return true;
    return getDetectionStatus(d) === currentFilter;
  });

  return (
    <AppContext.Provider
      value={{
        shelfs,
        detections: filteredDetections,
        currentFilter,
        setCurrentFilter,
        isDarkMode,
        toggleDarkMode: () => setIsDarkMode((d) => !d),
        currentUser,
        switchUser: (role) => setCurrentUser(profiles[role]),
        selectedSlot,
        setSelectedSlot,
        selectedThresholdProduct,
        setSelectedThresholdProduct,
        thresholdModalProduct,
        openThresholdModal: (productName: string) => setThresholdModalProduct(productName),
        closeThresholdModal: () => setThresholdModalProduct(null),
        loading,
        error,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used inside <AppProvider>");
  return ctx;
}
