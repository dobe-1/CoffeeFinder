import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Geomap } from './geomap';

describe('Geomap', () => {
  let component: Geomap;
  let fixture: ComponentFixture<Geomap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Geomap],
    }).compileComponents();

    fixture = TestBed.createComponent(Geomap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
