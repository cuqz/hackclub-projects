import { memo, useCallback } from "react";
import { useWorkflowStore } from "../../store/workflowStore";

const CATEGORIES = [
  { name: "Strategy", skills: ["Brand Architect"] },
  { name: "Design", skills: ["UI Artisan", "Image Alchemist"] },
  { name: "Development", skills: ["Code Forger", "Code Reviewer"] },
  { name: "Content", skills: ["Content Weaver", "Documentation Sage"] },
  { name: "Marketing", skills: ["SEO Oracle"] },
  { name: "Security", skills: ["Security Guardian"] },
];

const SKILL_ICONS: Record<string, string> = {
  "Brand Architect": "🎯",
  "UI Artisan": "🎨",
  "Image Alchemist": "🖼️",
  "Code Forger": "⚡",
  "Code Reviewer": "🔍",
  "Content Weaver": "✍️",
  "Documentation Sage": "📝",
  "SEO Oracle": "📈",
  "Security Guardian": "🔐",
};

let nodeCounter = 0;

function SkillPaletteComponent() {
  const currentWorkflow = useWorkflowStore((s) => s.currentWorkflow);
  const updateNodes = useWorkflowStore((s) => s.updateNodes);
  const skills = useWorkflowStore((s) => s.skills);
  const skillsArr = skills as any[];

  const handleAdd = useCallback((skillName: string) => {
    const skill = skillsArr.find((s: any) => s.name === skillName);
    if (!skill || !currentWorkflow) return;
    nodeCounter++;
    const id = `node_${Date.now()}_${nodeCounter}`;
    const newNode = {
      id,
      skillId: skill.id || id,
      label: skill.name,
      category: skill.category || "General",
      position: { x: 250 + (nodeCounter % 5) * 180, y: 100 + Math.floor(nodeCounter / 5) * 200 },
      config: {} as Record<string, string>,
      configFields: skill.config || [],
      status: "idle" as const,
    } as any;
    updateNodes([...currentWorkflow.nodes, newNode]);
  }, [skillsArr, currentWorkflow, updateNodes]);

  return (
    <div className="p-5">
      <div className="mb-6">
        <h3 className="text-sm font-semibold" style={{ color: "hsl(var(--text))" }}>Agent skills</h3>
        <p className="text-xs mt-0.5" style={{ color: "hsl(var(--muted))" }}>Click to add a node</p>
      </div>

      {CATEGORIES.map((cat) => (
        <div key={cat.name} className="mb-5">
          <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "hsl(var(--muted))" }}>
            {cat.name}
          </div>
          <div className="flex flex-col gap-1.5">
            {cat.skills.map((skillName) => (
              <button
                key={skillName}
                onClick={() => handleAdd(skillName)}
                className="flex items-center gap-2.5 w-full px-3 py-2.5 rounded-xl text-xs text-left transition-all duration-200 hover:translate-x-[2px]"
                style={{ background: "hsl(var(--bg))", border: "1px solid hsl(var(--stroke))", color: "hsl(var(--text))" }}
              >
                <span className="text-base">{SKILL_ICONS[skillName] || "✦"}</span>
                {skillName}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export const SkillPalette = memo(SkillPaletteComponent);
