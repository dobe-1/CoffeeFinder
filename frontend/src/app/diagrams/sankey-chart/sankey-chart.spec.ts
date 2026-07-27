import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SankeyChart } from './sankey-chart';

describe('SankeyChart', () => {
  let component: SankeyChart;
  let fixture: ComponentFixture<SankeyChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SankeyChart],
    }).compileComponents();

    fixture = TestBed.createComponent(SankeyChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
