//KINESIS CONSUMER API
const express = require('express');
const {
  KinesisClient,
  GetShardIteratorCommand,
  GetRecordsCommand,
  DescribeStreamCommand
} = require("@aws-sdk/client-kinesis");

const app = express();
const port = 3000;

async function getFilteredRecords(streamName, region, eventType) {
  const client = new KinesisClient({ region });

  const describe = await client.send(new DescribeStreamCommand({ StreamName: streamName }));
  const shardId = describe.StreamDescription.Shards[0].ShardId;

  const iteratorRes = await client.send(new GetShardIteratorCommand({
    StreamName: streamName,
    ShardId: shardId,
    ShardIteratorType: "TRIM_HORIZON"
  }));

  let iterator = iteratorRes.ShardIterator;
  const filtered = [];

  while (iterator) {
    const data = await client.send(new GetRecordsCommand({
      ShardIterator: iterator,
      Limit: 100
    }));

    for (const record of data.Records) {
      const payload = Buffer.from(record.Data).toString();
      try {
        const json = JSON.parse(payload);
        if (!eventType || json.event_type === eventType) {
          filtered.push(json);
        }
      } catch {
        // ignore invalid JSON
      }
    }

    iterator = data.NextShardIterator;
    if (data.Records.length === 0) break;
    await new Promise(r => setTimeout(r, 1000));
  }

  return filtered;
}

app.get('/consume', async (req, res) => {
  const { stream, region, event_type } = req.query;

  if (!stream || !region) {
    return res.status(400).json({ error: 'stream and region parameters are required' });
  }

  try {
    const records = await getFilteredRecords(stream, region, event_type);
    res.json({ count: records.length, records });
  } catch (err) {
    console.error('❌ Error consuming stream:', err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(port, () => {
  console.log(`🔥 Kinesis Consumer REST API running on port ${port}`);
});

module.exports = app;
