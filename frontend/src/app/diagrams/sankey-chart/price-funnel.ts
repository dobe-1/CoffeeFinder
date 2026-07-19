import { SankeyLink, SankeyNode } from './sankey-chart';

export interface FunnelCounts {
  totalShops: number;
  shopsWithWebsite: number;
  shopsWithPrices: number;
}

export function buildPriceFunnel(counts: FunnelCounts): {
  nodes: SankeyNode[];
  links: SankeyLink[];
} {
  const withWebsite = counts.shopsWithWebsite;
  const noWebsite = counts.totalShops - withWebsite;
  const withPrices = counts.shopsWithPrices;
  const noPrices = withWebsite - withPrices;

  const nodes: SankeyNode[] = [
    { name: 'Total shops', itemStyle: { color: '#6f4e37' } },
    { name: 'With website', itemStyle: { color: '#af764d' } },
    { name: 'No website', itemStyle: { color: '#c0392b' } },
    { name: 'With prices', itemStyle: { color: '#2e7d32' } },
    { name: 'No prices', itemStyle: { color: '#c0392b' } },
  ];

  const links: SankeyLink[] = [
    { source: 'Total shops', target: 'With website', value: withWebsite },
    { source: 'Total shops', target: 'No website', value: noWebsite },
    { source: 'With website', target: 'With prices', value: withPrices },
    { source: 'With website', target: 'No prices', value: noPrices },
  ].filter((link) => link.value > 0);

  return { nodes, links };
}
