import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  type Node,
  type Edge,
  type Connection,
  type OnNodesChange,
  type OnEdgesChange,
  MarkerType,
  addEdge,
} from "reactflow";
import "reactflow/dist/style.css";
import { useWorkflowStore } from "../../store/workflowStore";
import { SkillNode } from "./SkillNode";

const nodeTypes = { skill: SkillNode };

const defaultEdgeOptions = {
  style: { stroke: "rgba(255,255,255,0.12)", strokeWidth: 2 },
  markerEnd: { type: MarkerType.ArrowClosed, color: "rgba(255,255,255,0.2)", width: 16, height: 16 },
};

interface Props {
  onNodeClick: (event: any, node: Node) => void;
  onCanvasClick: () => void;
}

export function WorkflowCanvas({ onNodeClick, onCanvasClick }: Props) {
  const wf = useWorkflowStore((s) => s.currentWorkflow);
  const updateNodes = useWorkflowStore((s) => s.updateNodes);
  const updateEdges = useWorkflowStore((s) => s.updateEdges);

  // Properly map WorkflowNode -> ReactFlow Node (with data wrapper)
  const nodes: Node[] = useMemo(() => (wf?.nodes || []).map((n: any) => ({
    id: n.id,
    type: "skill",
    position: n.position,
    data: {
      // Support both new WorkflowNode format (flat) and old ReactFlow format (nested in data.*)
      label: n.label || n.data?.label || "",
      category: n.category || n.data?.category || "",
      config: n.config || n.data?.config || {},
      status: n.status || n.data?.status || "idle",
      outputType: n.outputType || n.data?.outputType || "text",
      configFields: n.configFields || n.data?.configFields || [],
    },
  })), [wf?.nodes]);

  const edges: Edge[] = useMemo(() => (wf?.edges || []).map((e: any) => ({
    ...e,
    markerEnd: { type: MarkerType.ArrowClosed, color: "rgba(255,255,255,0.2)", width: 16, height: 16 },
  })), [wf?.edges]);

  const onNodesChangeHandler: OnNodesChange = useCallback((changes) => {
    updateNodes(changes);
  }, [updateNodes]);

  const onEdgesChangeHandler: OnEdgesChange = useCallback((changes) => {
    updateEdges(changes);
  }, [updateEdges]);

  const onConnect = useCallback((conn: Connection) => {
    if (!edges) return;
    const newEdges = addEdge({ ...conn, markerEnd: { type: MarkerType.ArrowClosed, color: "rgba(255,255,255,0.2)", width: 16, height: 16 } }, edges);
    updateEdges(newEdges);
  }, [edges, updateEdges]);

  return (
    <div className="w-full h-full" style={{ background: "hsl(var(--bg))" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeHandler}
        onEdgesChange={onEdgesChangeHandler}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onCanvasClick}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        minZoom={0.1}
        maxZoom={2}
        deleteKeyCode="Backspace"
        multiSelectionKeyCode="Shift"
        snapToGrid
        snapGrid={[16, 16]}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="rgba(255,255,255,0.04)" />
        <Controls showInteractive={false} />
        <MiniMap
          nodeStrokeWidth={3}
          maskColor="rgba(0,0,0,0.85)"
          style={{
            background: "hsl(var(--surface))",
            border: "1px solid hsl(var(--stroke))",
            borderRadius: 12,
            overflow: "hidden",
          }}
        />
      </ReactFlow>
    </div>
  );
}
