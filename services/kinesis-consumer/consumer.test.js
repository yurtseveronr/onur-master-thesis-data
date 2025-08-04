jest.mock("@aws-sdk/client-kinesis", () => {
  const mockSend = jest.fn()
    .mockImplementationOnce(() => Promise.resolve({
      StreamDescription: { Shards: [{ ShardId: "mock-shard" }] }
    }))
    .mockImplementationOnce(() => Promise.resolve({
      ShardIterator: "mock-iterator"
    }))
    .mockImplementationOnce(() => Promise.resolve({
      Records: [
        { Data: Buffer.from(JSON.stringify({ event_type: "order", order_id: `ORD-${Math.floor(Math.random() * 1000)}` })) },
        { Data: Buffer.from(JSON.stringify({ event_type: "user", user_id: `USR-${Math.floor(Math.random() * 1000)}` })) }
      ],
      NextShardIterator: null
    }));

  return {
    KinesisClient: jest.fn(() => ({ send: mockSend })),
    DescribeStreamCommand: jest.fn(),
    GetShardIteratorCommand: jest.fn(),
    GetRecordsCommand: jest.fn()
  };
});

const request = require("supertest");
const app = require("./consumer_api");

describe("GET /consume", () => {
  it("✅ should return only filtered 'order' events and exit immediately if records exist", async () => {
    const response = await request(app).get("/consume")
      .query({
        stream: `dummy-stream-${Math.floor(Math.random() * 1000)}`,
        region: "us-east-1",
        event_type: "order"
      });

    expect(response.statusCode).toBe(200);
    expect(response.body.count).toBe(1);
    expect(response.body.records[0].event_type).toBe("order");
    expect(response.body.records[0].order_id).toMatch(/^ORD-/);
  });
});

// Force exit
setTimeout(() => {
  process.exit(0);
}, 2000);