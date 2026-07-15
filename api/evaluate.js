const fs = require('fs');
const path = require('path');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const mockPath = path.join(__dirname, '..', 'sample_data', 'mock_response.json');
  const payload = fs.existsSync(mockPath)
    ? JSON.parse(fs.readFileSync(mockPath, 'utf8'))
    : {
        status: 'ok',
        mock: true,
        review: {
          summary: 'Mock review: the document looks structurally sound and ready for a first pass.',
          score: 82,
          highlights: ['The upload was received successfully.'],
          nextSteps: ['Add clearer section headings.'],
        },
      };

  res.status(200).json(payload);
};
