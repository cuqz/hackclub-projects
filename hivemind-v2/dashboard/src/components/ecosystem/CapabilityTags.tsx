import { Tag, Sparkles, ShieldAlert, Award, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { EcosystemTag } from '@/api/ecosystem';

interface CapabilityTagsProps {
  tags: EcosystemTag[];
}

/** 标签分类的色彩 + 图标映射 */
function categoryStyle(category: string): { className: string; label: string; Icon: typeof Tag } {
  switch (category) {
    case 'capability':
      return {
        className:
          'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-800',
        label: '能力',
        Icon: Sparkles,
      };
    case 'maturity':
      return {
        className:
          'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300 dark:border-emerald-800',
        label: '成熟度',
        Icon: Award,
      };
    case 'risk':
      return {
        className:
          'bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-900/40 dark:text-rose-300 dark:border-rose-800',
        label: '风险',
        Icon: ShieldAlert,
      };
    default:
      return {
        className: 'bg-muted text-muted-foreground border-border',
        label: category,
        Icon: Tag,
      };
  }
}

/** 来源中文映射 */
const SOURCE_LABELS: Record<string, string> = {
  github_topic: 'GitHub Topic',
  auto_rule: '自动规则',
  llm: 'LLM 推断',
  manual: '人工标注',
};

/**
 * 能力标签展示 — 按 category 分组，confidence 决定不透明度。
 */
export function CapabilityTags({ tags }: CapabilityTagsProps) {
  if (!tags || tags.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Tag className="h-4 w-4" aria-hidden="true" />
            能力标签
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground flex items-center gap-2">
          <Info className="h-4 w-4 shrink-0" aria-hidden="true" />
          暂无能力标签 — 等待 ecosystem-tagger 处理。
        </CardContent>
      </Card>
    );
  }

  // 按 category 分组
  const grouped = tags.reduce<Record<string, EcosystemTag[]>>((acc, t) => {
    (acc[t.category] ??= []).push(t);
    return acc;
  }, {});

  // 分类显示顺序
  const categoryOrder = ['capability', 'maturity', 'risk'];
  const sortedCategories = Object.keys(grouped).sort((a, b) => {
    const ai = categoryOrder.indexOf(a);
    const bi = categoryOrder.indexOf(b);
    return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Tag className="h-4 w-4" aria-hidden="true" />
          能力标签 ({tags.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {sortedCategories.map((cat) => {
          const { className, label, Icon } = categoryStyle(cat);
          return (
            <div key={cat} className="space-y-1.5">
              <div className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                {label}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {grouped[cat].map((tag) => {
                  const opacity = Math.max(0.55, tag.confidence);
                  const sourceLabel = SOURCE_LABELS[tag.source] ?? tag.source;
                  return (
                    <Badge
                      key={tag.tag_id}
                      variant="outline"
                      className={`text-xs border ${className}`}
                      style={{ opacity }}
                      title={`${tag.description ?? tag.name} · ${sourceLabel} · 置信度 ${(tag.confidence * 100).toFixed(0)}%`}
                    >
                      {tag.name}
                      <span className="ml-1 text-[10px] opacity-70">
                        {(tag.confidence * 100).toFixed(0)}%
                      </span>
                    </Badge>
                  );
                })}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
