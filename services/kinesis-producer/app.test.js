jest.mock('aws-sdk', () => {
  const putRecordMock = jest.fn().mockReturnValue({
    promise: jest.fn().mockRejectedValue(new Error("Kinesis failed"))
  });

  return {
    Kinesis: jest.fn(() => ({
      putRecord: putRecordMock
    })),
    config: {
      update: jest.fn()
    }
  };
});

// MOCK yukarıda TANIMLI olmalı, ondan sonra import edilmeli
const request = require('supertest');
const app = require('./app');

describe('POST /produce', () => {
  it('should return 400 if required parameters are missing', async () => {
    const response = await request(app)
      .post('/produce')
      .send({});
    expect(response.statusCode).toBe(400);
    expect(response.body.error).toMatch(/required/);
  });

  it('should return 500 if Kinesis fails (mocked)', async () => {
    const response = await request(app)
      .post('/produce')
      .send({
        streamName: "test-stream",
        partitionKey: "abc",
        region: "us-east-1",
        data: { test: true }
      });

    expect(response.statusCode).toBe(500);
    expect(response.body.error).toBe("Kinesis failed");
  });
});
