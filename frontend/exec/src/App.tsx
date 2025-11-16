import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ShelfDetail from "./pages/ShelfDetail";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />}>
          <Route path="shelf/:cameraId?" element={<ShelfDetail />} />
        </Route>
      </Routes>
    </Router>
  );
}
