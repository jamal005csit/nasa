import express from 'express';
import cors from 'cors';
const app = express(); app.use(cors()); app.use(express.json());

// Your frontend calls THIS instead of NASA directly
app.get('/api/region', async (req, res) => {
  const { lat, lon, year = 2026 } = req.query;
  try {
    const url = `https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,PRECTOTCORR,RH2M,WS2M&community=RE&longitude=${lon}&latitude=${lat}&format=JSON`;
    const data = await (await fetch(url)).json();
    res.json({ lat:+lat, lon:+lon, year:+year, power: data.properties.parameter, source:'NASA POWER' });
  } catch(e){ res.status(502).json({ error:'NASA POWER failed' }); }
});

app.get('/api/fires', async (req, res) => { // FIRMS key stays SECRET on server
  const key = process.env.FIRMS_MAP_KEY;
  const url = `https://firms.modaps.eosdis.nasa.gov/api/area/csv/${key}/VIIRS_SNPP_NRT/-180,-90,180,90/2`;
  res.type('text/csv').send(await (await fetch(url)).text());
});

app.get('/api/events', async (req,res)=>{
  res.json(await (await fetch('https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=100')).json());
});

app.listen(4000, ()=>console.log('EARTH//NEXT backend → http://localhost:4000'));