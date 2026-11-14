# AppEEARS results drop zone

Put the unzipped contents of each AppEEARS Area Sample request here:

```
science/data/raw/appeears/
├── nile_delta.geojson          ← upload this to AppEEARS for the Delta request
├── sahara_interior.geojson     ← upload this for the Sahara request
├── nile_delta/                 ← AppEEARS writes the Delta result here
│   ├── MOD13C2.061_*_doy*_aid0001.nc   (one NetCDF per month, already subset to this polygon)
│   └── ...
└── sahara_interior/            ← AppEEARS writes the Sahara result here
    └── ...
```

Each `.nc` is already clipped to the polygon, so these files are tiny (~tens of KB each,
few MB total per region).
