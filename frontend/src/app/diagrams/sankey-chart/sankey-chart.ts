import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  effect,
  input,
  viewChild,
} from '@angular/core';
import * as echarts from 'echarts/core';
import { SankeyChart as SankeySeries } from 'echarts/charts';
import { TitleComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([SankeySeries, TitleComponent, TooltipComponent, CanvasRenderer]);


export interface SankeyNode {
  name: string;
  itemStyle?: { color?: string };
  label?: { position?: 'left' | 'right' | 'top' | 'bottom' | 'inside' };
}

export interface SankeyLink {
  source: string;
  target: string;
  value: number;
}


@Component({
  selector: 'app-sankey-chart',
  standalone: true,
  imports: [],
  templateUrl: './sankey-chart.html',
  styleUrl: './sankey-chart.css',
})
export class SankeyChart implements AfterViewInit, OnDestroy {
  readonly nodes = input.required<SankeyNode[]>();
  readonly links = input.required<SankeyLink[]>();
  readonly chartTitle = input<string>('');

  private readonly container = viewChild.required<ElementRef<HTMLDivElement>>('chart');
  private chart?: echarts.ECharts;
  private resizeObserver?: ResizeObserver;

  constructor() {
    effect(() => {
      const option = this.buildOption(this.nodes(), this.links(), this.chartTitle());
      this.chart?.setOption(option, true);
    });
  }

  ngAfterViewInit() {
    const element = this.container().nativeElement;
    this.chart = echarts.init(element);
    this.chart.setOption(this.buildOption(this.nodes(), this.links(), this.chartTitle()), true);

    this.resizeObserver = new ResizeObserver(() => this.chart?.resize());
    this.resizeObserver.observe(element);
  }

  ngOnDestroy() {
    this.resizeObserver?.disconnect();
    this.chart?.dispose();
  }

  private buildOption(
    nodes: SankeyNode[],
    links: SankeyLink[],
    title: string,
  ): echarts.EChartsCoreOption {

    const depth = this.computeDepths(nodes, links);
    const maxDepth = Math.max(0, ...depth.values());
    const data = nodes.map((node) => {
      if (node.label) {
        return node;
      }
      const position: 'left' | 'right' = depth.get(node.name) === maxDepth ? 'left' : 'right';
      return { ...node, label: { position } };
    });

    return {
      title: title ? { text: title, left: 'center', top: 4, textStyle: { fontSize: 14 } } : undefined,
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        valueFormatter: (value: number) => `${value}`,
      },
      series: [
        {
          type: 'sankey',
          nodeAlign: 'left',
          data,
          links,
          emphasis: { focus: 'adjacency' },
          lineStyle: { color: 'gradient', curveness: 0.5 },
          label: { fontSize: 12 },
          top: title ? 48 : 12,
          bottom: 12,
          left: 12,
          right: 12,
        },
      ],
    };
  }

  private computeDepths(nodes: SankeyNode[], links: SankeyLink[]): Map<string, number> {
    const depth = new Map<string, number>(nodes.map((node) => [node.name, 0]));
    let changed = true;
    while (changed) {
      changed = false;
      for (const link of links) {
        const candidate = (depth.get(link.source) ?? 0) + 1;
        if (candidate > (depth.get(link.target) ?? 0)) {
          depth.set(link.target, candidate);
          changed = true;
        }
      }
    }
    return depth;
  }
}
