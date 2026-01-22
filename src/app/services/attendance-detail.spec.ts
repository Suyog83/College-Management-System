import { TestBed } from '@angular/core/testing';

import { AttendanceDetail } from './attendance-detail';

describe('AttendanceDetail', () => {
  let service: AttendanceDetail;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AttendanceDetail);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
