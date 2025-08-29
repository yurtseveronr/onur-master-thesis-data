//KINESIS PRODUCER API
const express = require('express');
const AWS = require('aws-sdk');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/produce', async (req, res) => {
  const {
    streamName,
    partitionKey,
    region,
    data
  } = req.body;

  if (!streamName || !partitionKey || !region || !data) {
    return res.status(400).json({ error: 'streamName, partitionKey, region, and data are required.' });
  }

  AWS.config.update({ region });
  const kinesis = new AWS.Kinesis();

  const params = {
    Data: Buffer.from(JSON.stringify(data)),
    PartitionKey: partitionKey,
    StreamName: streamName
  };

  try {
    const result = await kinesis.putRecord(params).promise();
    res.status(200).json({ message: 'Record sent to Kinesis', result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Eğer bu dosya doğrudan çalıştırılıyorsa, sunucuyu başlat
if (require.main === module) {
  app.listen(port, () => {
    console.log(`Kinesis producer API running on port ${port}`);
  });
}

// Testlerde kullanılmak üzere dışa aktar
module.exports = app;
