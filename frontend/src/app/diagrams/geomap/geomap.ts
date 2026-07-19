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
import {
  GeoComponent,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([
  ScatterSeries,
  GeoComponent,
  VisualMapComponent,
  TitleComponent,
  TooltipComponent,
  CanvasRenderer,
]);

export interface GeoScatterPoint {
  name: string;
  lon: number;
  lat: number;
  value: number | null;
  dimmed?: boolean;
}

@Component({
  selector: 'app-geomap',
  imports: [],
  templateUrl: './geomap.html',
  styleUrl: './geomap.css',
})
export class Geomap implements AfterViewInit, OnDestroy {
  readonly geoJson = input.required<object | null>();
  readonly mapName = input<string>('map');
  readonly points = input.required<GeoScatterPoint[]>();
  readonly valueName = input<string>('');
  readonly title = input<string>('');

  private readonly container = viewChild.required<ElementRef<HTMLDivElement>>('chart');
  private chart?: echarts.ECharts;
  private resizeObserver?: ResizeObserver;

  constructor() {
    effect(() => {
      const geoJson = this.geoJson();
      const points = this.points();
      const mapName = this.mapName();
      const valueName = this.valueName();
      const title = this.title();
      if (!this.chart || !geoJson) {
        return;
      }
      echarts.registerMap(mapName, geoJson as Parameters<typeof echarts.registerMap>[1]);
      this.chart.setOption(this.buildOption(mapName, points, valueName, title), true);
    });
  }

  ngAfterViewInit() {
    const element = this.container().nativeElement;
    this.chart = echarts.init(element);

    this.resizeObserver = new ResizeObserver(() => this.chart?.resize());
    this.resizeObserver.observe(element);
  }

  ngOnDestroy() {
    this.resizeObserver?.disconnect();
    this.chart?.dispose();
  }

  private buildOption(
    mapName: string,
    points: GeoScatterPoint[],
    valueName: string,
    title: string,
  ): echarts.EChartsCoreOption {
    const reliable = points.filter((point) => !point.dimmed && point.value !== null);
    const dimmed = points.filter((point) => point.dimmed);

    const values = reliable.map((point) => point.value as number);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 1;

    const toData = (list: GeoScatterPoint[]) =>
      list.map((point) => ({ name: point.name, value: [point.lon, point.lat, point.value] }));

    return {
      title: title ? { text: title, left: 'center', top: 4, textStyle: { fontSize: 14 } } : undefined,
      tooltip: {
        trigger: 'item',
        formatter: (params: { name: string; value: [number, number, number | null] }) => {
          const value = params.value?.[2];
          const shown = value == null ? '—' : `${value} ${valueName}`.trim();
          return `${params.name}<br/>${shown}`;
        },
      },
      geo: {
        map: mapName,
        roam: false,
        silent: true,
        itemStyle: { areaColor: '#f6f1e7', borderColor: '#8a7a63' },
      },
      visualMap: {
        type: 'continuous',
        min,
        max,
        dimension: 2,
        seriesIndex: 0,
        calculable: true,
        left: 'left',
        bottom: 12,
        text: [`${max.toFixed(2)}`, `${min.toFixed(2)}`],
        inRange: { color: ['#e6d9c8', '#c8a06a', '#6f4e37'] },
      },
      series: [
        {
          name: 'reliable',
          type: 'scatter',
          coordinateSystem: 'geo',
          symbolSize: 10,
          data: toData(reliable),
        },
        {
          name: 'dimmed',
          type: 'scatter',
          coordinateSystem: 'geo',
          symbolSize: 7,
          itemStyle: { color: '#c9c2b6' },
          data: toData(dimmed),
        },
      ],
    };
  }
}