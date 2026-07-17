import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Landing } from "./pages/Landing";
import { Dashboard } from "./pages/Dashboard";
import { WorkflowEditor } from "./pages/WorkflowEditor";
import { Pricing } from "./pages/Pricing";
import { useEffect } from "react";
import { useWorkflowStore } from "./store/workflowStore";

export default function App() {
  const loadSkills = useWorkflowStore((s) => s.loadSkills);
  useEffect(() => { loadSkills(); }, [loadSkills]);
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workflow/:id" element={<WorkflowEditor />} />
        <Route path="/pricing" element={<Pricing />} />
      </Route>
    </Routes>
  );
}
