// This is a Vercel serverless function that proxies API requests to the backend
export default async function handler(req, res) {
  const backendUrl = process.env.REACT_APP_API_URL;
  
  if (!backendUrl) {
    return res.status(500).json({ 
      error: 'Backend URL not configured',
      message: 'Please set REACT_APP_API_URL environment variable in Vercel'
    });
  }

  const path = req.url.replace('/api-proxy', '');
  const targetUrl = `${backendUrl}/api${path}`;

  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        ...req.headers,
        'Content-Type': req.headers['content-type'] || 'application/json',
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? req.body : undefined,
    });

    const contentType = response.headers.get('content-type');
    let data;

    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    res.status(response.status);
    res.setHeader('Content-Type', contentType || 'application/json');
    
    return res.json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    return res.status(500).json({ 
      error: error.message,
      details: 'Failed to reach backend'
    });
  }
}
