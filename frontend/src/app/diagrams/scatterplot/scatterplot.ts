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
import { ScatterChart as ScatterSeries } from 'echarts/charts';
import { GridComponent, TitleComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([ScatterSeries, GridComponent, TitleComponent, TooltipComponent, CanvasRenderer]);

export interface ScatterPoint {
  x: number;
  y: number;
  name?: string;
  itemStyle?: { color?: string };
}

@Component({
  selector: 'app-scatterplot',
  standalone: true,
  imports: [],
  templateUrl: './scatterplot.html',
  styleUrl: './scatterplot.css',
})
export class Scatterplot implements AfterViewInit, OnDestroy {
  readonly points = input.required<ScatterPoint[]>();
  readonly xName = input<string>('');
  readonly yName = input<string>('');
  readonly chartTitle = input<string>('');

  private readonly container = viewChild.required<ElementRef<HTMLDivElement>>('chart');
  private chart?: echarts.ECharts;
  private resizeObserver?: ResizeObserver;

  constructor() {
    effect(() => {
      const option = this.buildOption(
        this.points(),
        this.xName(),
        this.yName(),
        this.chartTitle(),
      );
      this.chart?.setOption(option, true);
    });
  }

  ngAfterViewInit() {
    const element = this.container().nativeElement;
    this.chart = echarts.init(element);
    this.chart.setOption(
      this.buildOption(this.points(), this.xName(), this.yName(), this.chartTitle()),
      true,
    );

    this.resizeObserver = new ResizeObserver(() => this.chart?.resize());
    this.resizeObserver.observe(element);
  }

  ngOnDestroy() {
    this.resizeObserver?.disconnect();
    this.chart?.dispose();
  }

  private buildOption(
    points: ScatterPoint[],
    xName: string,
    yName: string,
    title: string,
  ): echarts.EChartsCoreOption {
    return {
      title: title ? { text: title, left: 'center', top: 4, textStyle: { fontSize: 14 } } : undefined,

      grid: { left: 70, right: 24, top: title ? 48 : 24, bottom: 56 },
      tooltip: {
        trigger: 'item',
        formatter: (params: { value: [number, number]; name: string }) => {
          const [x, y] = params.value;
          const label = params.name ? `${params.name}<br/>` : '';
          return `${label}${xName || 'x'}: ${x}<br/>${yName || 'y'}: ${y}`;
        },
      },
      xAxis: {
        type: 'value',
        name: xName,
        nameLocation: 'middle',
        nameGap: 32,
        scale: true,
      },
      yAxis: {
        type: 'value',
        name: yName,
        nameLocation: 'middle',
        nameGap: 48,
        scale: true,
      },
      series: [
        {
          type: 'scatter',
          symbolSize: 11,
          data: points.map((point) => ({
            value: [point.x, point.y],
            name: point.name,
            itemStyle: point.itemStyle,
          })),
        },
      ],
    };
  }
}
