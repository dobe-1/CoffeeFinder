import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Scatterplot } from './scatterplot';

describe('Scatterplot', () => {
  let component: Scatterplot;
  let fixture: ComponentFixture<Scatterplot>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Scatterplot],
    }).compileComponents();

    fixture = TestBed.createComponent(Scatterplot);
    fixture.componentRef.setInput('points', []);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
