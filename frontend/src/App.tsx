import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MainLayout } from "./components/layout/MainLayout";
import { ProductionPage } from "./pages/ProductionPage";
import { ToastContainer } from "./components/ui/ToastContainer";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* ── Main app routes ──────────────────────── */}
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/daftar/foam" replace />} />
            <Route path="daftar/:section" element={<ProductionPage />} />
            <Route path="*" element={<Navigate to="/daftar/foam" replace />} />
          </Route>
        </Routes>
        <ToastContainer />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
