import { useQueryClient } from '@tanstack/react-query';
import { Check, ChevronsUpDown, Folder, FolderOpen } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Skeleton } from '@/components/ui/skeleton';
import { useProject } from '@/context/ProjectContext';
import { useProjects } from '@/api/projects';

/**
 * 生态库项目筛选器 — 选择「查看哪个项目的生态库」。每个项目有自己方向的生态仓档案。
 *
 * ⚠️ 作用域：这是 **ecosystem 专属** 的项目筛选，只用于 ecosystem 列表页 (/ecosystem)。
 *    切勿放回全局 Header / components/layout —— 历史教训 (v1.6.0)：本组件原名
 *    `ProjectSwitcher`、放在 components/layout、挂在右上角 Header，并在 client.ts 被注释为
 *    「Global project context」，导致被误当成全局应用切换器；而实际上除 ecosystem 外没有
 *    任何页面真正消费它（任务墙/报告等各有页内筛选）。命名+目录已纠正以锁死语义。
 *    若将来真要做全局项目切换，请另建组件，不要复用本组件。
 *
 * 切换时：
 *   1. ProjectContext.switchProject 同步更新 api/client 的 module-level state
 *      (X-Project-Id header) — 在 setState 之前写入避免 race
 *   2. invalidateQueries — 刷新查询让 ecosystem 列表按新项目重拉
 *      (注：当前 X-Project-Id 会附加到所有请求，故切换也会影响其它 header-scoped 调用；
 *       这是已知遗留，未来可改为仅对 ecosystem 请求附加 per-call header)
 */
export function EcosystemProjectFilter() {
  const { projectId, projectName, switchProject, clearProject } = useProject();
  const { data, isLoading } = useProjects();
  const qc = useQueryClient();

  const projects = data?.data ?? [];

  /**
   * 项目列表本身不按 X-Project-Id 隔离，切换时不要让它跟着 refetch
   * (避免抖动)。其它所有 query (ecosystem/tasks/projects/{id}/...) 都需刷新。
   */
  const invalidateProjectScopedQueries = () => {
    void qc.invalidateQueries({
      predicate: (q) => {
        const k = q.queryKey;
        if (Array.isArray(k) && k[0] === 'projects' && k.length === 1) return false;
        return true;
      },
    });
  };

  const handleSelect = (id: string, path: string, name: string) => {
    if (id === projectId) return;
    switchProject(id, path, name);
    invalidateProjectScopedQueries();
  };

  const handleClear = () => {
    if (projectId === null) return;
    clearProject();
    invalidateProjectScopedQueries();
  };

  if (isLoading) {
    return <Skeleton className="h-8 w-48" />;
  }

  const triggerLabel = projectName ?? '全部项目';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="切换生态库项目"
        className="inline-flex items-center gap-1.5 h-8 px-3 max-w-[260px] rounded-md border border-input bg-background text-sm font-medium shadow-xs hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors"
      >
        {projectId ? (
          <FolderOpen className="h-3.5 w-3.5 text-primary shrink-0" aria-hidden="true" />
        ) : (
          <Folder className="h-3.5 w-3.5 text-muted-foreground shrink-0" aria-hidden="true" />
        )}
        <span className="truncate">{triggerLabel}</span>
        <ChevronsUpDown className="h-3 w-3 text-muted-foreground shrink-0" aria-hidden="true" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72">
        <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">切换生态库项目</div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleClear}>
          <span className="flex items-center gap-2 flex-1">
            <Folder className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
            <span className="text-sm">全部项目</span>
          </span>
          {projectId === null && <Check className="h-3.5 w-3.5" aria-hidden="true" />}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        {projects.length === 0 ? (
          <div className="px-2 py-3 text-xs text-muted-foreground text-center">暂无项目</div>
        ) : (
          projects.map((p) => (
            <DropdownMenuItem
              key={p.id}
              onClick={() => handleSelect(p.id, p.root_path, p.name)}
            >
              <span className="flex items-center gap-2 flex-1 min-w-0">
                <FolderOpen
                  className={`h-3.5 w-3.5 shrink-0 ${p.id === projectId ? 'text-primary' : 'text-muted-foreground'}`}
                  aria-hidden="true"
                />
                <span className="flex flex-col min-w-0">
                  <span className="text-sm truncate">{p.name}</span>
                  {p.root_path && (
                    <span className="text-[10px] text-muted-foreground truncate">{p.root_path}</span>
                  )}
                </span>
              </span>
              {p.id === projectId && <Check className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />}
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
