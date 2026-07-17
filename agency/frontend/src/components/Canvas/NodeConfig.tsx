import { memo, useCallback } from "react";
import { useWorkflowStore } from "../../store/workflowStore";
import type { Node } from "reactflow";

interface Props {
  selectedNode: Node | null;
}

function NodeConfigComponent({ selectedNode }: Props) {
  const updateNodeConfig = useWorkflowStore((s) => s.updateNodeConfig);

  const handleChange = useCallback((key: string, value: string) => {
    if (!selectedNode?.id) return;
    const currentConfig = (selectedNode.data as any)?.config || {};
    updateNodeConfig(selectedNode.id, { ...currentConfig, [key]: value });
  }, [selectedNode, updateNodeConfig]);

  if (!selectedNode) {
    return (
      <div className="p-5 text-center">
        <div className="text-2xl mb-2 opacity-30">👆</div>
        <p className="text-xs" style={{ color: "hsl(var(--muted))" }}>Select a node to configure</p>
      </div>
    );
  }

  const config = (selectedNode.data as any)?.config || {};
  const configFields = (selectedNode.data as any)?.configFields || [];

  return (
    <div className="p-5">
      <div className="mb-5">
        <h3 className="text-sm font-semibold" style={{ color: "hsl(var(--text))" }}>
          {(selectedNode.data as any)?.label || "Node"}
        </h3>
        <p className="text-[10px] uppercase tracking-wider font-semibold mt-0.5" style={{ color: "hsl(var(--muted))" }}>
          {(selectedNode.data as any)?.category || "General"} node
        </p>
      </div>

      {configFields.length === 0 ? (
        <div className="p-4 rounded-xl text-xs text-center" style={{ background: "hsl(var(--bg))", color: "hsl(var(--muted))" }}>
          No configuration options
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {configFields.map((field: any) => (
            <div key={field.key}>
              <label className="block text-xs font-medium mb-1.5" style={{ color: "hsl(var(--text-secondary))" }}>
                {field.label}
              </label>
              {field.type === "textarea" ? (
                <textarea
                  value={config[field.key] || ""}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2.5 rounded-xl text-xs outline-none resize-none transition-all duration-200 focus:border-accent/30"
                  style={{ background: "hsl(var(--bg))", border: "1px solid hsl(var(--stroke))", color: "hsl(var(--text))" }}
                  placeholder={field.placeholder || ""}
                />
              ) : (
                <input
                  value={config[field.key] || ""}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl text-xs outline-none transition-all duration-200"
                  style={{ background: "hsl(var(--bg))", border: "1px solid hsl(var(--stroke))", color: "hsl(var(--text))" }}
                  placeholder={field.placeholder || ""}
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export const NodeConfig = memo(NodeConfigComponent);
